import html  # Replaces `cgi` for escaping in Python 3
import time
import sys
import traceback
from collections import defaultdict
import util

class Grades:
    "A data structure for project grades, along with formatting code to display them"
    def __init__(self, projectName, questionsAndMaxesList, edxOutput=False, muteOutput=False):
        self.questions = [el[0] for el in questionsAndMaxesList]
        self.maxes = dict(questionsAndMaxesList)
        self.points = Counter()
        self.messages = {q: [] for q in self.questions}
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True  # Sanity checks
        self.currentQuestion = None  # Which question we're grading
        self.edxOutput = edxOutput
        self.mute = muteOutput
        self.prereqs = defaultdict(set)

        print(f'Starting on {self.start[0]}-{self.start[1]} at {self.start[2]:02d}:{self.start[3]:02d}:{self.start[4]:02d}')

    def addPrereq(self, question, prereq):
        self.prereqs[question].add(prereq)

    def grade(self, gradingModule, exceptionMap={}, bonusPic=False):
        completedQuestions = set()
        for q in self.questions:
            print(f'\nQuestion {q}')
            print('=' * (9 + len(q)))
            print()
            self.currentQuestion = q

            incompleted = self.prereqs[q].difference(completedQuestions)
            if len(incompleted) > 0:
                prereq = incompleted.pop()
                print(f"""*** NOTE: Make sure to complete Question {prereq} before working on Question {q},
*** because Question {q} builds upon your answer for Question {prereq}.
""")
                continue

            if self.mute:
                util.mutePrint()
            try:
                util.TimeoutFunction(getattr(gradingModule, q), 300)(self)  # Call the question's function
            except Exception as inst:
                self.addExceptionMessage(q, inst, traceback)
                self.addErrorHints(exceptionMap, inst, q[1])
            except BaseException:
                self.fail('FAIL: Terminated with a string exception.')
            finally:
                if self.mute:
                    util.unmutePrint()

            if self.points[q] >= self.maxes[q]:
                completedQuestions.add(q)

            print(f'\n### Question {q}: {self.points[q]}/{self.maxes[q]} ###\n')

        print(f'\nFinished at {time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}')
        print("\nProvisional grades\n==================")

        for q in self.questions:
            print(f'Question {q}: {self.points[q]}/{self.maxes[q]}')
        print('------------------')
        print(f'Total: {self.points.totalCount()}/{sum(self.maxes.values())}')
        if bonusPic and self.points.totalCount() == 25:
            print("""
                     ALL HAIL GRANDPAC.
              LONG LIVE THE GHOSTBUSTING KING.
                  (artwork omitted for brevity)
""")
        print("""
Your grades are NOT yet registered.  To register your grades, make sure
to follow your instructor's guidelines to receive credit on your project.
""")

        if self.edxOutput:
            self.produceOutput()

    def addExceptionMessage(self, q, inst, traceback):
        self.fail(f'FAIL: Exception raised: {inst}')
        self.addMessage('')
        for line in traceback.format_exc().split('\n'):
            self.addMessage(line)

    def addErrorHints(self, exceptionMap, errorInstance, questionNum):
        typeOf = str(type(errorInstance))
        questionName = 'q' + questionNum
        errorHint = ''

        if exceptionMap.get(questionName):
            questionMap = exceptionMap.get(questionName)
            if questionMap.get(typeOf):
                errorHint = questionMap.get(typeOf)

        if exceptionMap.get(typeOf):
            errorHint = exceptionMap.get(typeOf)

        if not errorHint:
            return ''

        for line in errorHint.split('\n'):
            self.addMessage(line)

    def produceOutput(self):
        with open('edx_response.html', 'w') as edxOutput:
            edxOutput.write("<div>")

            total_possible = sum(self.maxes.values())
            total_score = sum(self.points.values())
            checkOrX = '<span class="incorrect"/>'
            if total_score >= total_possible:
                checkOrX = '<span class="correct"/>'
            header = f"""
                <h3>
                    Total score ({total_score} / {total_possible})
                </h3>
            """
            edxOutput.write(header)

            for q in self.questions:
                name = q[1] if len(q) == 2 else q
                checkOrX = '<span class="incorrect"/>' if self.points[q] != self.maxes[q] else '<span class="correct"/>'
                messages = f"<pre>{html.escape('\n'.join(self.messages[q]))}</pre>"
                output = f"""
                <div class="test">
                  <section>
                  <div class="shortform">
                    Question {q} ({self.points[q]}/{self.maxes[q]}) {checkOrX}
                  </div>
                <div class="longform">
                  {messages}
                </div>
                </section>
              </div>
              """
                edxOutput.write(output)

            edxOutput.write("</div>")

        with open('edx_grade', 'w') as edxOutput:
            edxOutput.write(str(self.points.totalCount()))

    def fail(self, message, raw=False):
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self):
        self.points[self.currentQuestion] = 0

    def addPoints(self, amt):
        self.points[self.currentQuestion] += amt

    def deductPoints(self, amt):
        self.points[self.currentQuestion] -= amt

    def assignFullCredit(self, message="", raw=False):
        self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
        if message:
            self.addMessage(message, raw)

    def addMessage(self, message, raw=False):
        if not raw:
            if self.mute:
                util.unmutePrint()
            print('*** ' + message)
            if self.mute:
                util.mutePrint()
            message = html.escape(message)
        self.messages[self.currentQuestion].append(message)

    def addMessageToEmail(self, message):
        print(f"WARNING**** addMessageToEmail is deprecated {message}")
        for line in message.split('\n'):
            pass


class Counter(dict):
    """
    Dict with default 0
    """
    def __getitem__(self, idx):
        return dict.get(self, idx, 0)

    def totalCount(self):
        return sum(self.values())
