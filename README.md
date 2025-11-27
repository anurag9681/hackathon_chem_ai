<h1 align="center">🧪 Chemical Engineering AI Assistant</h1>
<h3 align="center">Generate PFDs • Analyze Uploaded PFDs • Optimize Processes • Perform HAZOP Analysis</h3>

<p align="center">
This repository contains an advanced AI model for Chemical Engineering applications.
It can generate Process Flow Diagrams (PFDs), interpret uploaded diagrams, perform
process optimization, and create detailed HAZOP/HAZID safety analyses.
</p>

<hr>

<h2>🚀 Key Features</h2>

<ul>
  <li><strong>🔧 PFD Generation</strong>
    <ul>
      <li>Create PFDs from process descriptions or step-by-step instructions.</li>
      <li>Generate PFDs for any famous industrial process (Haber process, methanol synthesis, cracking, etc.).</li>
    </ul>
  </li>

  <li><strong>🖼️ PFD Analysis</strong>
    <ul>
      <li>Upload a PFD image and ask any question about the diagram.</li>
      <li>Understands unit operations, equipment, streams, and system behavior.</li>
    </ul>
  </li>

  <li><strong>⚙️ Process Optimization</strong>
    <ul>
      <li>Energy optimization and heat-integration suggestions.</li>
      <li>Process layout improvement and bottleneck removal.</li>
      <li>Proposes cost-efficient and performance-improving modifications.</li>
    </ul>
  </li>

  <li><strong>⚠️ HAZOP / HAZID Study</strong>
    <ul>
      <li>Generate complete HAZOP tables for any process.</li>
      <li>Includes deviations, causes, consequences, safeguards, and recommendations.</li>
    </ul>
  </li>
</ul>

<hr>

<h2>📂 Repository Structure</h2>

<pre>
├── src/
│   ├── pfd_generator.py          # PFD generation engine
│   ├── pfd_analyzer.py           # PFD interpretation module
│   ├── high_quality_generator.py # Quality improvement of generated image
│   ├── equipment_symbols.py      # Chemical engineering symbols for PFD generation
│   ├── llm_processor_for_app.py  # LLM configuration
│   └── Chatbot_finalizing.py     # Streamlit UI
├── README.md
└── requirements.txt
</pre>

<hr>

<h2>🛠️ Installation</h2>

<pre>
git clone https://github.com/anurag9681/hackathon_chem_ai.git
pip install -r requirements.txt
</pre>

<hr>

<h2>📘 Examples</h2>

<p>See the <code>examples/</code> directory for sample outputs including:</p>
<ul>
  <li>PFD generations</li>
  <li>Diagram-based Q&A</li>
  <li>Process optimization summaries</li>
  <li>HAZOP worksheets</li>
</ul>

<hr>

<h2>🤝 Contributing</h2>

<p>Contributions are welcome! You can open issues, submit pull requests,
or suggest new features or chemical process datasets.</p>

<hr>

<h2>🛡️ Disclaimer</h2>
<p>
This project is intended for research and educational use.
It should <strong>not</strong> replace certified engineering judgment.
Always verify AI-generated results before using them in real industrial settings.
</p>

<hr>

<h2 align="center">⭐ If you like this project, consider starring the repository!</h2>
