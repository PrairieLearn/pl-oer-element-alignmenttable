import sys
import os

sys.path.append(os.path.abspath("../serverFilesCourse/sequenceAlignment_autograder"))
from sequenceAlignment_autograder.paired_HMM import generate_paired_sequences
from sequenceAlignment_autograder.local_alignment import local_alignment
from sequenceAlignment_autograder.global_alignment import global_alignment
from sequenceAlignment_autograder.fitting_alignment import fitting_alignment



def generate(data):
    # Generating randomized sequences that are used for all questions
    data["params"]["v"], data["params"]["w"] = generate_paired_sequences(4)

    # Computing the "correct answer" used to pre-fill the table and path displayed for Q1
    data["correct_answers"]["q1"] = global_alignment(data["params"]["v"], data["params"]["w"])

    # Assigning the actual answer strings for the string inputs for Q1 
    data["params"]["str1"], data["params"]["str2"] = data["correct_answers"]["q1"][1].split("\n")
    
    # Computing the correct answer used to pre-fill the table and grade the path for Q2
    data["correct_answers"]["q2"] = fitting_alignment(data["params"]["v"], data["params"]["w"])
    
    # Computing the correct answer used to grade the table and path for Q3
    data["correct_answers"]["q3"] = local_alignment(data["params"]["v"], data["params"]["w"])
