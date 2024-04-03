from common import F, FunctionalCommitment, LootBoxInput, verifyEvalProofRaw
from pywebio.input import input, input_group, actions, NUMBER, TEXT
from pywebio.output import put_text, put_code, put_button
from pywebio.session import run_js
from pywebio import start_server
import PRB
import inspect


def post_process(y):
    m = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    star3 = 10
    star2 = 30
    star1 = 100
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
        x = int.from_bytes(randomness, "big")
        put_text(f"Convert to decimal: {x}")
    else:
        x = int(input("Enter x:", type=TEXT))

    put_text(f"Evaluate at x = {x}")
    y, pi = fc.evalAndProofRaw(x)
    put_text(f"Evaluated value y = f(x) = {y}")
    put_text(f"Evaluation Proof: {pi}")
    assert verifyEvalProofRaw(commitment, F(x), y, pi)

    put_text("The y will be going through post-processing to get the result:")
    put_code(
        inspect.getsource(post_process), language="python"
    )  # publicize the post_process function

    def run_post_process_client():
        py = f"""
from browser import alert
{inspect.getsource(post_process)}
res = post_process({y})
alert(res)
"""
        js = """
__BRYTHON__.runPythonSource(py)
"""
        run_js(js, py=py)

    put_button("Run this on client side", onclick=run_post_process_client)
    put_text(f"You got: {post_process(y)}")

    while True:
        info = input_group(
            "Verify (Can only be done on the server side currently)",
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
