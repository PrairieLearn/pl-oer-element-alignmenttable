import random

# Function to choose the next state based on current state
def next_state(current_state, transition_prob):
    transitions = transition_prob[current_state]
    states = list(transitions.keys())
    probabilities = list(transitions.values())
    return random.choices(states, weights=probabilities, k=1)[0]


# Function to emit symbols based on the current state
def emit_symbols(state, match_emission_prob, insert_emission_prob):
    if state == "M":
        pairs = list(match_emission_prob.keys())
        probabilities = list(match_emission_prob.values())
        emission = random.choices(pairs, weights=probabilities, k=1)[0]
        return emission
    elif state == "I":
        # Emit a character from sequence 1 and a gap in sequence 2
        nucleotides = list(insert_emission_prob.keys())
        probabilities = list(insert_emission_prob.values())
        nucleotide = random.choices(nucleotides, weights=probabilities, k=1)[0]
        return (nucleotide, "-")
    elif state == "J":
        # Emit a gap in sequence 1 and a character from sequence 2
        nucleotides = list(insert_emission_prob.keys())
        probabilities = list(insert_emission_prob.values())
        nucleotide = random.choices(nucleotides, weights=probabilities, k=1)[0]
        return ("-", nucleotide)


# Function to generate paired sequences
def generate_paired_sequences(length, alphabet=["A", "C", "G", "T"], match_prob = 0.3, delta = 0.2, epsilon = 0.1):
    sequence1 = []
    sequence2 = []
    state_sequence = []
    match_emission_prob = {}
    # Probability for a match
    mismatch_prob = 1 - match_prob  # Probability for a mismatch

    for x in alphabet:
        for y in alphabet:
            if x == y:
                match_emission_prob[(x, y)] = match_prob / len(alphabet)  # Divide equally among matches
            else:
                match_emission_prob[(x, y)] = (
                    mismatch_prob / (len(alphabet) * (len(alphabet) - 1))
                )  # Divide equally among mismatches

    # Emission probabilities for Insert states (I and J)
    insert_emission_prob = {
        c: 1 / 4 for c in alphabet
    }  # Equal probability for each character

    transition_prob = {
        "M": {"M": 1 - 2 * delta, "I": delta, "J": delta},
        "I": {"I": epsilon, "M": 1 - epsilon},
        "J": {"J": epsilon, "M": 1 - epsilon},
    }

    # Start from state 'M'
    current_state = "M"
    while len(sequence1) < length or len(sequence2) < length:
        state_sequence.append(current_state)
        # Emit symbols based on current state
        s1, s2 = emit_symbols(current_state, match_emission_prob, insert_emission_prob)
        if s1 != "-":
            sequence1.append(s1)
        if s2 != "-":
            sequence2.append(s2)
        # Transition to next state
        current_state = next_state(current_state, transition_prob)
    if len(sequence1) <= len(sequence2):
        return "".join(sequence1), "".join(sequence2)
    else:
        return "".join(sequence2), "".join(sequence1)