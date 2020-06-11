from iota.crypto.types import Seed  #importing PyOTA library to interact with

NewSeed = Seed.random()
print(NewSeed)
print("Length: %s" % len(NewSeed))