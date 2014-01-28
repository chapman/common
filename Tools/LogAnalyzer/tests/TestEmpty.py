from LogAnalyzer import Test,TestResult
import DataflashLog


class TestEmpty(Test):
	'''test for empty or near-empty logs'''

	def __init__(self):
		self.name = "Empty"
		
	def run(self, logdata):
		self.result = TestResult()
		self.result.status = TestResult.StatusType.PASS

		# TODO: implement test for empty or near-empty logs (i.e. vehicle hasn't flown greater than X distance or Y height, or for Z duration with throttle above some threshold)
		