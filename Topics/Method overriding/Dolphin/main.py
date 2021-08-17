class Mammal:
    def __init__(self):
        self.bio_class = "mammal"

    def greet(self):
        print("I am a {}!".format(self.bio_class))


# create class Dolphin here
class Dolphin(Mammal):
    def greet(self):
        super().greet()
        print("I am a dolphin!")
