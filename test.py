from common import F, FunctionalCommitment, LootBoxInput, verifyEvalProofRaw
from pywebio.input import input, input_group, actions, NUMBER, TEXT
from pywebio.output import (
    put_text,
    put_markdown,
    put_code,
    put_button,
    use_scope,
    clear,
)
from pywebio.session import run_js
from pywebio import start_server
import PRB
import inspect


def mapping_function(randomness: bytes):
    from hashlib import sha256

    m = 21888242871839275222246405745257275088548364400416034343698204186575808495617  # field modulus
    while True:
        randomness = sha256(randomness).digest()
        yield int.from_bytes(randomness, "big") % m


def post_process(y):
    m = 21888242871839275222246405745257275088548364400416034343698204186575808495617  # field modulus
    star3 = 10  # number of 3 star cards
    star2 = 30  # number of 2 star cards
    star1 = 100  # number of 1 star cards
    p = int(y) / m
    if p < 0.03:
        pp = p / 0.03
        idx = int(pp * star3)
        return f"3 start: card #{idx}"
    if p < 0.2:
        pp = (p - 0.03) / 0.17
        idx = int(pp * star2)
        return f"2 start: card #{idx}"
    pp = (p - 0.2) / 0.8
    idx = int(pp * star1)
    return f"1 star: card #{idx}"


def main():
    run_js(
        """
window.loadscript = function loadscript({ src, type, content }) {
    const script = document.createElement('script')
    if (type) script.type = type
    if (src) script.src = src
    if (content) script.text = content
    document.head.appendChild(script)
    return new Promise((resolve, reject) => {
        script.onload = resolve
        script.onerror = reject
    })
}
loadscript({ src: 'https://cdn.jsdelivr.net/npm/brython@3.12.2/brython.min.js' })
loadscript({ src: 'https://cdn.jsdelivr.net/npm/brython@3.12.2/brython_stdlib.js' })
           """
    )
    fc = FunctionalCommitment(5, randomCoeff=True)
    commitment = fc.getCommitment()
    with use_scope("setup"):
        put_markdown("# Setup Phase")
        put_text(f"FC: {commitment}")

    with use_scope("randomness_contribution"):
        put_markdown("# Randomness Contribution Phase")
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
            put_text("Getting verified PRB randomness, please wait...")
            randomness = PRB.eval(contribution)
            put_text(f"Verified PRB Randomness: {randomness.hex()}")
        else:
            randomness = input(
                "Enter your fake PRB randomness (random string):", type=TEXT
            ).encode()
            put_text(f"Fake PRB Randomness: {randomness.hex()}")

        put_text(
            "The randomness will be mapped to inputs using the following function:"
        )
        put_code(
            inspect.getsource(mapping_function), language="python"
        )  # publicize the mapping_function function

    inputs_generator = mapping_function(randomness)

    with use_scope("evaluation"):
        put_markdown("# Evaluation Phase")
        with use_scope("evaluation_history"):
            put_markdown("## Evaluation History")
        with use_scope("evaluation_loop"):
            keep_running = True
            n_tries = 1
            while keep_running:
                clear()
                put_markdown(f"## #{n_tries} Evaluation Loop")
                x = next(inputs_generator)
                put_text(f"Evaluate at x = {x}")
                y, pi = fc.evalAndProofRaw(x)
                put_text(f"Evaluated value y = f(x) = {y}")
                put_text(f"Evaluation Proof: {pi}")
                assert verifyEvalProofRaw(commitment, F(x), y, pi)

                put_text(
                    "The y will be going through post-processing to get the result:"
                )
                put_code(
                    inspect.getsource(post_process), language="python"
                )  # publicize the post_process function

                def run_post_process_client():
                    py = f"from browser import alert\n{inspect.getsource(post_process)}\nres = post_process({y})\nalert(res)\n"
                    js = "__BRYTHON__.runPythonSource(py)"
                    run_js(js, py=py)

                put_button(
                    "Run this on client side (powered by Brython)",
                    onclick=run_post_process_client,
                )
                put_text(f"You got: {post_process(y)}")

                keep_running = actions(
                    "Do you want to try another evaluation?",
                    [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ],
                )
                if keep_running:
                    put_text(
                        f"#{n_tries} output generated from mapping function: {x = }",
                        scope="evaluation_history",
                    )
                    n_tries += 1

    with use_scope("verification"):
        put_markdown("# Verification Phase")
        while True:
            info = input_group(
                "Verify (Currently this sends the data to the server for verification)",
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
    start_server(main, host="0.0.0.0", port=12121, debug=True)
