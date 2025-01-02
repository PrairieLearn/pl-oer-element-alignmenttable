import random

# Define the alphabet
alphabet = ["A", "C", "G", "T"]

# Define emission probabilities for the Match state (P)
# Let's assume equal probability for matches and lower for mismatches
match_emission_prob = {}
match_prob = 0.3  # Probability for a match
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

# Adjusted Delta (gap opening probability)
delta = 0.2  # Smaller delta, less likely to open a gap

# Adjusted Epsilon (gap extension probability)
epsilon = 0.1  # Larger epsilon, more likely to extend a gap

transition_prob = {
    "M": {"M": 1 - 2 * delta, "I": delta, "J": delta},
    "I": {"I": epsilon, "M": 1 - epsilon},
    "J": {"J": epsilon, "M": 1 - epsilon},
}

# Function to choose the next state based on current state
def next_state(current_state):
    transitions = transition_prob[current_state]
    states = list(transitions.keys())
    probabilities = list(transitions.values())
    return random.choices(states, weights=probabilities, k=1)[0]


# Function to emit symbols based on the current state
def emit_symbols(state):
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
def generate_paired_sequences(length):
    sequence1 = []
    sequence2 = []
    state_sequence = []

    # Start from state 'M'
    current_state = "M"
    while len(sequence1) < length or len(sequence2) < length:
        state_sequence.append(current_state)
        # Emit symbols based on current state
        s1, s2 = emit_symbols(current_state)
        if s1 != "-":
            sequence1.append(s1)
        if s2 != "-":
            sequence2.append(s2)
        # Transition to next state
        current_state = next_state(current_state)
    if len(sequence1) <= len(sequence2):
        return "".join(sequence1), "".join(sequence2), state_sequence
    else:
        return "".join(sequence2), "".join(sequence1), state_sequence

def main():
    # Example usage
    seq_length = 3  # Desired length of sequences
    seq1, seq2, states = generate_paired_sequences(seq_length)

    print("Sequence 1:", seq1)
    print("Sequence 2:", seq2)
    print("State Path:", "".join(states))

if __name__ == "__main__":
    main()