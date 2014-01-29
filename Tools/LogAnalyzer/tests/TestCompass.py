from LogAnalyzer import Test,TestResult
import DataflashLog


class TestCompass(Test):
	'''test for compass offsets and throttle interference'''

	def __init__(self):
		self.name = "Compass"

	def run(self, logdata):
		self.result = TestResult()
		self.result.status = TestResult.StatusType.PASS

		# TODO: should max compass offsets be 150 or 250 on Pixhawk?
		# quick test that compass offset parameters are within recommended range (+/- 150)
		maxOffset   = 150
		compassOfsX = logdata.parameters["COMPASS_OFS_X"]
		compassOfsY = logdata.parameters["COMPASS_OFS_Y"]
		compassOfsZ = logdata.parameters["COMPASS_OFS_Z"]
		#print "MAG params: %.2f %.2f %.2f" % (compassOfsX,compassOfsY,compassOfsZ)
		if abs(compassOfsX) > maxOffset or abs(compassOfsY) > maxOffset or abs(compassOfsZ) > maxOffset:
			self.result.status = TestResult.StatusType.FAIL
			self.result.statusMessage = "Large compass off params (X:%.2f, Y:%.2f, Z:%.2f)" % (compassOfsX,compassOfsY,compassOfsZ)

		# check for excessive compass offsets using MAG data if present
		# TODO: MAG log values seem to be constant, do we need to check them?
		if "MAG" in logdata.channels:
			errMsg = "Large MAG offset data - "
			err = False
			#print "MAG min/max xyz... %.2f %.2f %.2f %.2f %.2f %.2f " % (logdata.channels["MAG"]["OfsX"].min(), logdata.channels["MAG"]["OfsX"].max(), logdata.channels["MAG"]["OfsY"].min(), logdata.channels["MAG"]["OfsY"].min(), logdata.channels["MAG"]["OfsZ"].min(), logdata.channels["MAG"]["OfsZ"].max())
			if logdata.channels["MAG"]["OfsX"].max() >  maxOffset:
				errMsg = errMsg + "X: %.2f" % logdata.channels["MAG"]["OfsX"].max()
				err = True
			if logdata.channels["MAG"]["OfsX"].min() < -maxOffset:
				errMsg = errMsg + "X: %.2f" % logdata.channels["MAG"]["OfsX"].min()
				err = True
			if logdata.channels["MAG"]["OfsY"].max() >  maxOffset:
				errMsg = errMsg + "Y: %.2f" % logdata.channels["MAG"]["OfsY"].max()
				err = True
			if logdata.channels["MAG"]["OfsY"].min() < -maxOffset:
				errMsg = errMsg + "Y: %.2f" % logdata.channels["MAG"]["OfsY"].min()
				err = True
			if logdata.channels["MAG"]["OfsZ"].max() >  maxOffset:
				errMsg = errMsg + "Z: %.2f" % logdata.channels["MAG"]["OfsZ"].max()
				err = True
			if logdata.channels["MAG"]["OfsZ"].min() < -maxOffset:
				errMsg = errMsg + "Z: %.2f" % logdata.channels["MAG"]["OfsZ"].min()
				err = True
			if err:
				self.result.status = TestResult.StatusType.FAIL
				self.result.statusMessage = errMsg

		# TODO: check for compass/throttle interference. Need to add mag_field to logging, or calc our own from MAG data if present
		# TODO: can we derive a compassmot percentage from the params? Fail if >30%?				
