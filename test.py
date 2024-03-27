from common import F, FunctionalCommitment, LootBoxInput, verifyEvalProofRaw
from pywebio.input import input, input_group, actions, NUMBER, TEXT
from pywebio.output import put_text
from pywebio import start_server
import PRB


def post_process(y):
    p = int(y) / int(F.m)
    if p < 0.03:
        return "3 star"
    if p < 0.2:
        return "2 star"
    return "1 star"


def main():
    yesprb = actions(
        "Do you want to contribute to PRB?",
        [
            {"label": "Yes", "value": True},
            {"label": "No", "value": False},
        ],
    )
    if yesprb:
        entropy = input("Enter entropy:", type=TEXT)
        contribution = PRB.contribute(entropy.encode())
        put_text(f"Contribution: {contribution}")

    fc = FunctionalCommitment(5, randomCoeff=True)
    commitment = fc.getCommitment()
    put_text(f"FC: {commitment}")
    if yesprb:
        put_text("Getting verified PRB randomness, please wait...")
        randomness = PRB.eval(contribution)
        put_text(f"Verified PRB Randomness: {randomness.hex()}")
        x = int.from_bytes(randomness, "big") % int(F.m)
    else:
        x = int(input("Enter x:", type=TEXT))

    put_text(f"Evalute at x = {x}")
    y, pi = fc.evalAndProofRaw(x)
    put_text(f"Evaluated value: {y}")
    put_text(f"Proof: {pi}")
    assert verifyEvalProofRaw(commitment, F(x), y, pi)

    put_text(f"You got: {post_process(y)}")

    while True:
        info = input_group(
            "Verify",
            [
                input(
                    "Commitment",
                    type=TEXT,
                    value=str(commitment),
                    name="c",
                    readonly=True,
                ),
                input("x", type=TEXT, value=str(x), name="x"),
                input("y", type=TEXT, value=str(y), name="y"),
                input("Proof", type=TEXT, value=str(pi), name="pi", readonly=True),
            ],
        )
        if verifyEvalProofRaw(commitment, F(int(info["x"])), F(int(info["y"])), pi):
            put_text(f"Verify Success with x = {info['x']}, y = {info['y']}")
        else:
            put_text(f"Verify Failed with x = {info['x']}, y = {info['y']}")


if __name__ == "__main__":
    start_server(main, host="0.0.0.0", port=12121)
