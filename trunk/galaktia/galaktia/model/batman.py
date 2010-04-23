
class Batman:
	""" SARA BARA BARA BARA BATMAN
	SARA BARA BARA BARA BATMAN
	BATMAN
	BAAATMANNN """

	def __init__(self, *args, **kwargs):
		if args or kwargs:
			print "Batman is not bound by parameters."

	def getID(self):
		return "Bruce Wayne"

	def getVehicle(self):
		return "Batmobile"

	def getTools(self):
		if self.batbelt:
			return self.batbelt
		else
			raise NotImplementedError

    def __repr__(self):
        return "I'm Batman"

    # OK, guys! Let's cut the joke. It ain't funny.

