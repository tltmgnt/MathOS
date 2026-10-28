"""
MathOS — Local Web Interface.

Provides a browser interface for solving supported
linear equations without paid AI services.
"""

import html
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from mathos.core import MathOS


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MathOS</title>
<style>
body {
    font-family: system-ui, sans-serif;
    background: #101827;
    color: white;
    max-width: 700px;
    margin: 50px auto;
    padding: 20px;
}
h1 { color: #69b7ff; }
input, button {
    padding: 14px;
    font-size: 16px;
    border-radius: 8px;
}
input {
    width: 90%;
    margin-bottom: 15px;
}
button {
    background: #2389ef;
    color: white;
    border: none;
    cursor: pointer;
}
pre {
    background: #1e293b;
    padding: 20px;
    border-radius: 10px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}
</style>
</head>
<body>
<h1>MathOS</h1>
<p>Mathematical Reasoning & Verification</p>
<section style="background:#1e293b;padding:20px;border-radius:10px;margin:20px 0;">
  <h2 style="color:#69b7ff;">Ω Welfare Optimization</h2>

  <p>WE THE PEOPLE Ω — Universal Welfare Framework</p>

  <div style="overflow-x:auto;text-align:center;padding:15px 0;">
    <math display="block" xmlns="http://www.w3.org/1998/Math/MathML">
      <msubsup>
        <mi>𝒲</mi>
        <mi>Ω</mi>
        <mo>*</mo>
      </msubsup>
      <mo>=</mo>
      <munder>
        <mo>max</mo>
        <mrow><mi>π</mi><mo>∈</mo><mi>Π</mi></mrow>
      </munder>
      <msubsup>
        <mo>∫</mo><mn>0</mn><mi>T</mi>
      </msubsup>
      <msup>
        <mi>e</mi>
        <mrow><mo>−</mo><mi>ρ</mi><mi>t</mi></mrow>
      </msup>
      <mo>[</mo>
      <munderover>
        <mo>∑</mo>
        <mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow>
        <mi>n</mi>
      </munderover>
      <msub><mi>w</mi><mi>i</mi></msub>
      <msub><mi>U</mi><mi>i</mi></msub>
      <mo>(</mo><mi>t</mi><mo>)</mo>
      <mo>−</mo><mi>λ</mi><mi>R</mi><mo>(</mo><mi>t</mi><mo>)</mo>
      <mo>−</mo><mi>μ</mi><mi>G</mi><mo>(</mo><mi>t</mi><mo>)</mo>
      <mo>]</mo>
      <mi>d</mi><mi>t</mi>
    </math>
  </div>

  <p>Maximizing weighted welfare while accounting for risk
  and governance costs over time.</p>
</section>
<form method="POST">
<input
    name="problem"
    placeholder="Example: 2x + 5 = 13"
    required
>
<br>
<button type="submit">Solve & Verify</button>
</form>

<pre>{result}</pre>

<p>Offline mathematical engine — no API key required.</p>
</body>
</html>
"""


class MathOSHandler(BaseHTTPRequestHandler):

    def send_page(self, result="Enter an equation to begin."):
        content = PAGE.replace(
    "{result}",
    html.escape(result)
).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(content))
        )
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        self.send_page()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))

        if length > 4096:
            self.send_error(413, "Request too large")
            return

        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)
        problem = form.get("problem", [""])[0]

        try:
            result = MathOS().solve(
                problem,
                domain="mathematics",
            )
            output = json.dumps(
                result.to_dict(),
                indent=2,
            )
        except ValueError as error:
            output = f"Error: {error}"

        self.send_page(output)

def main():
    host = os.environ.get("MATHOS_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    server = HTTPServer(
        (host, port),
        MathOSHandler,
    )

    print(f"MathOS running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
    
