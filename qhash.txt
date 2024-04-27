from qiskit import QuantumCircuit, transpile
from qiskit.visualization import circuit_drawer
from scipy.stats import chisquare
from qiskit_ibm_runtime.fake_provider import FakeVigo, FakeAlgiers, FakeAthens, FakeHanoi, FakeBoeblingen

backend = FakeBoeblingen()


def angle_encoding_hash_8bit(n_qubits, bit_string, x, y, x1, y1):

    """
    Hash the input bit string using the parameterized quantum circuit.

    Args:
        bit_string (str): A binary bit string, e.g., '1010'.
        x (float): The angle to add to qubits when the corresponding bit is '1'.
        y (float): The angle to add to qubits when the corresponding bit is '0'.

    Returns:
        int: The hash value as an integer.
    """
    # Assuming bit_string is already a string of bits (like '10100101')
    qc = QuantumCircuit(n_qubits)
    for j in range(8):
        if j < 4:
            if bit_string[7 - j] == '1':
                qc.rx(x, j)  # Apply an Rx gate with angle x if the j-th bit is 1
            else:
                qc.rx(y, j)  # Apply an Rx gate with angle y if the j-th bit is 0
        else:
            if bit_string[7 - j] == '1':
                qc.ry(x1, j - 4)  # Apply a Ry gate with angle x1 if the j-th bit is 1
            else:
                qc.ry(y1, j - 4)  # Apply a Ry gate with angle y1 if the j-th bit is 0

    for i in range(n_qubits - 1):
        qc.cx(i + 1, i)  # Apply CNOT gates between adjacent qubits

    qc.measure_all()
    compiled_circuit = transpile(qc, optimization_level=1)
    return simulate(compiled_circuit)

def simulate(circuit):
    device_backend = FakeBoeblingen()
    transpiled_circuit = transpile(circuit, device_backend)
    job = device_backend.run(transpiled_circuit)
    result = job.result()
    counts = result.get_counts()
    most_sampled_outcome = max(counts, key=lambda k: counts[k])
    return int(most_sampled_outcome, 2)

def start_qhash(data):
    n_qubits = 4
    x, y, x1, y1 = 3.14159265359, 0, 0, 3.14159265359
    try:
        # Convert integer input to an 8-bit binary string
        bit_string = bin(int(data))[2:].zfill(8)
        hash_value = angle_encoding_hash_8bit(n_qubits, bit_string, x, y, x1, y1)
        hash_bit_string = bin(hash_value)[2:].zfill(8)  # Assuming the hash fits within n_qubits bits
        return hash_bit_string
    except ValueError as e:
        print(f"Error: {e}")

def user_input_to_hash():
    n_qubits = 4
    x, y, x1, y1 = 3.14159265359, 0, 0, 3.14159265359
    user_input = input("Enter an integer to hash: ")  # Prompting user input
    try:
        # Convert integer input to an 8-bit binary string
        bit_string = bin(int(user_input))[2:].zfill(8)
        hash_value = angle_encoding_hash_8bit(n_qubits, bit_string, x, y, x1, y1)
        hash_bit_string = bin(hash_value)[2:].zfill(8)  # Assuming the hash fits within n_qubits bits
        print(f"Hash value for input '{user_input}' is: {hash_bit_string}")

    except ValueError as e:
        print("Invalid input. Please enter a valid integer.")
        print(f"Error: {e}")

if __name__ == "__main__":
    user_input_to_hash()