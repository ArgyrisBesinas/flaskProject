from utility import snippet_management
from utility import job_management
from datetime import datetime
import tokenize
import io
import random


class Snippet:
    def __init__(self, desc, code, source):
        self.desc = desc
        self.code = code
        self.source = source
        self.size = len(code.split("\n"))
        self.words = set([t.string.lower() for t in tokenize.tokenize(io.BytesIO(desc.encode('utf-8')).readline) if t.type==1])

        inputs = list()
        outputs = list()
        depth = 0
        prev_token = None
        for token in tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline):
            if token.string == '(':
                depth += 1
            elif token.string == ')':
                depth -= 1
            elif token.string == '=':
                if depth == 0:
                    outputs.append(prev_token)
            elif token.type == 1 and (prev_token is None or prev_token.string != '.'):
                inputs.append(token)
            prev_token = token

        def tmin(t1, t2):
            if t1[0] < t2[0]:
                return t1
            if t1[0] > t2[0]:
                return t2
            if t1[1] < t2[1]:
                return t1
            return t2

        def teq(t1, t2):
            return t1[0] == t2[0] and t1[1] == t2[1]

        pos = dict()
        for t in inputs:
            pos[t.string] = tmin(pos.get(t.string, (float('inf'), -1)), t.start)
        for t in outputs:
            pos[t.string] = tmin(pos.get(t.string, (float('inf'), -1)), t.start)

        self.outputs = set([t.string for t in outputs if teq(pos[t.string], t.start)])
        self.inputs = set([t.string for t in inputs])-self.outputs

    def print(self):
        print(self.code)
        print("INPUTS", self.inputs)
        print("OUTPUTS", self.outputs)


class Code:
    def __init__(self, desc, implementations=None):
        self.words = set([t.string.lower() for t in tokenize.tokenize(io.BytesIO(desc.encode('utf-8')).readline) if t.type==1])
        self.implementations = list() if implementations is None else implementations

    def overlap(self, snippet: Snippet):
        specs = len(self.words)-len(self.words - snippet.words)
        if specs == 0:
            return -float("inf")
        return specs - 0.1*snippet.size

    def add(self, snippet: Snippet):
        self.words -= snippet.words
        self.implementations.append(snippet)

    def sort(self):
        transfer = [[len(i.outputs)-len(i.outputs-j.inputs)
                     for j in self.implementations] for i in self.implementations]
        n = len(self.implementations)
        original = {i: i for i in range(n)}
        if n >= 2:
            for _ in range(n**2):
                i1 = random.randint(0, n-2)
                i2 = random.randint(i1+1, n-1)
                dtransfers = 0
                dtransfers += transfer[original[i1]][original[i2]]
                dtransfers -= transfer[original[i2]][original[i1]]
                for pos in range(i1+1, i2):
                    dtransfers += transfer[original[i1]][original[pos]]
                    dtransfers -= transfer[original[pos]][original[i1]]
                    dtransfers -= transfer[original[i2]][original[pos]]
                    dtransfers += transfer[original[pos]][original[i2]]
                if dtransfers < 0:
                    original[i1], original[i2] = original[i2], original[i1]
        self.implementations = [self.implementations[original[pos]] for pos in range(n)]


def start_synthesis_pysynth(job_id, text):
    job_management.edit_job_by_id(job_id, "Running", info="Searching", progress_percent=0)

    # search snippets
    found = list()
    result = Code(text)
    for word in result.words:
        for entry in snippet_management.search_snippets(word, None, 0):
            found.append(Snippet(entry["description"], entry["code"],
                                 (entry["snippet_source_id"], entry["snippet_local_id"])))

    original_remaining_words = len(result.words)
    job_management.edit_job_by_id(job_id, None, info="Fitting", progress_percent=0)

    for _ in range(100):
        prev_remaining_words = len(result.words)
        # find best entry
        best_snippet = None
        best_snippet_overlap = -float("inf")
        for snippet in found:
            overlap = result.overlap(snippet)
            if overlap > best_snippet_overlap:
                best_snippet = snippet
        # add best entry to solution
        if best_snippet is not None:
            # best_snippet.print()
            result.add(best_snippet)

        result.sort()
        # update job output
        job_management.delete_job_outputs([job_id])
        for snippet in result.implementations:
            job_management.insert_job_output(job_id, snippet.code, *snippet.source)

        # cancel if required
        if job_management.get_job_details_by_id(job_id)["status"] == "Cancelling...":
            job_management.edit_job_by_id(job_id, "Cancelled", info="Cancelled by user")
            return

        # update progress
        job_management.edit_job_by_id(job_id, "Running", info="Fitting",
                                      progress_percent=100 - int(len(result.words) * 100 / original_remaining_words))
        if len(result.words) == prev_remaining_words:
            break

    # notify about completion
    job_management.edit_job_by_id(job_id, "Completed", info="Completed", progress_percent=100,
                                  date_end=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
