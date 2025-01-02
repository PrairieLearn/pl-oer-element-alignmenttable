import sys
import os

sys.path.append(os.path.abspath("../serverFilesCourse/sequenceAlignment_autograder"))
from sequenceAlignment_autograder.paired_HMM import generate_paired_sequences
from sequenceAlignment_autograder.local_alignment import local_align
from sequenceAlignment_autograder.global_alignment import global_alignment
from sequenceAlignment_autograder.fitting_alignment import fitting_align



def generate(data):
    data["params"]["v"], data["params"]["w"], _ = generate_paired_sequences(4)

    ###### Quesiton 1 ########
    data["correct_answers"]["q1"] = global_alignment(data["params"]["v"], data["params"]["w"])
    data["params"]["str1"], data["params"]["str2"] = global_alignment(data["params"]["v"], data["params"]["w"])[1].split("\n")
    
    ###### Quesiton 2 ########
    data["correct_answers"]["q2"] = fitting_align(data["params"]["v"], data["params"]["w"])
    data["params"]["int1"] = fitting_align(data["params"]["v"], data["params"]["w"])[3]
    
    ###### Quesiton 3 ########
    data["correct_answers"]["q3"] = local_align(data["params"]["v"], data["params"]["w"])
