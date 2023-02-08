import random


def verifyCode():
    num1 = random.randint(1, 99)
    num2 = random.randint(1, 99)
    return (num1, num2)
