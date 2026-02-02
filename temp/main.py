from flask import Flask, render_template_string
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
import tempfile
import os
import subprocess
import tempfile
from bs4 import BeautifulSoup

app = Flask(__name__)

LATEX_SOURCE = r"""
%-------------------------
% Resume in Latex
% Author : Sourabh Bajaj
% License : MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[pdftex]{hyperref}
\usepackage{fancyhdr}
\usepackage{multirow}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.375in}
\addtolength{\evensidemargin}{-0.375in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[2]{
  \item\small{
    \textbf{#1}{: #2 \vspace{-2pt}}
  }
}

\newcommand{\resumeItemNH}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}\vspace{-4pt}}

\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*,label={}]}
\newcommand{\resumeSubHeadingListStartBullets}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}}

\usepackage{array}
\makeatletter
\newcommand\HUGE{\@setfontsize\Huge{38}{47}} 
\newcolumntype{L}{>{\hb@xt@\z@\bgroup}l<{\hss\egroup}}
\newcolumntype{C}{>{\centering\arraybackslash}c}
\newcolumntype{R}{>{\hb@xt@\z@\bgroup\hss}r<{\egroup}}
\makeatother

%-------------------------------------------
%%%%%%  CV STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING-----------------
\begin{tabular*}{\textwidth}{L@{\extracolsep{\fill}}C@{\extracolsep{\fill}}R}
  \href{mailto:email@gatech.edu}{email@gatech.edu} &
  \multirow{2}{*}{\Huge \textbf{John Smith}} &
  \href{https://personal-website.com}{https://personal-website.com} \\
  (123) 456-7890 & & US Citizen
\end{tabular*}

%-----------EDUCATION-----------------
\section{Education }
  \resumeSubHeadingListStart
    \resumeSubheading
      {Georgia Institute of Technology}{Atlanta, GA}
      {B.S. \& M.S. in Computer Science, GPA: 3.9/4.0}{Aug 2018 -- May 2022}
      \resumeItemListStart
        \resumeItem{Concentrations}{Machine Learning \& Information Internetworks}
        \resumeItem{Coursework}
          {Data Structures \& Algorithms, Object-Oriented Programming, Objects \& Software Design, Computer Organization,  Systems \& Networks, Design of Algorithms, Database Systems, Statistics, Applied Combinatorics}
      \resumeItemListEnd
  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------------
\section{Work Experience}
  \resumeSubHeadingListStart
  \resumeSubheading
      {NCR Corporation}{Atlanta, GA}
      {Software Engineering Intern}{Jun 2020 -- Aug 2020}

      \resumeItemListStart
        \resumeItemNH{Developed a new natural language processing feature for the Apiary malware analysis framework.}
        \resumeItemNH{Created new web-pages, RESTful API-endpoints and search features to better display results to users.}
        \resumeItemNH{Interfaced with MongoDB and Elasticsearch databases to access data, prototype new scripts and store results.}
        \resumeItemNH{Wrote extensive unit tests to ensure future functionality and updated Docker files for smarter deployment.}
      \resumeItemListEnd
    \resumeSubheading
      {Georgia Tech Research Institute}{Atlanta, GA}
      {Research Assistant}{May 2019 -- Dec 2019}
      \resumeItemListStart
        \resumeItemNH{Wrote novel algorithms to create 3D visualizations of the seafloor using LiDAR data collected from a plane.}
        \resumeItemNH{Developed new display features for a proprietary 3-D data visualization software, using C++.}
        \resumeItemNH{Compiled my results and submitted a paper to the SPIE DCS academic conference.}
      \resumeItemListEnd
    \resumeSubheading
      {NASA Glenn Research Center}{Cleveland, OH}
      {Research Assistant}{May 2018 -- Jun 2018}
      \resumeItemListStart
        \resumeItemNH{Tested a machine learning algorithm's memory usage in a Arduino by training a small car to avoid obstacles.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd
  
%-----------PROJECTS-----------------
\section{Projects}
  \resumeSubHeadingListStartBullets
    \resumeSubItem{CS4400 Group Project: Food Truck Webapp}
      {A webapp used for organizing Food Trucks. Designed the SQL database schema, including details about location, menu and customer data. Built the backend using Node.js, Express and MySQL. Used React.js and bootstrap to create an appealing frontend.}
    \resumeSubItem{HackGT Hackathon Project: ``Alexa Freestyle"}
      {Used a song lyric API and deep machine learning to generate new songs from existing lyrics. Connected Alexa to Amazon Web Service's ``Lambda" service to handle user requests and exceptions. Utilized an AWS ``EC2" instance to host a Flask server to run our algorithm efficiently and cache results.}
    \resumeSubItem{CS2340 Group Project: ``RISK"}
      {A multiplayer webapp version of the boardgame ``RISK". Built the front-end with Vue.js and Bootstrap. Used a Websocket API to connect to a Play Framework backend.}
  \resumeSubHeadingListEnd
  
%-----------EXTRACURRICULARS-----------------
\section{Involvement}
  \resumeSubHeadingListStartBullets
    \resumeSubItem{Georgia Tech Automotive Research Lab}
      {Software Team Lead for the student lead autonomous car research group. Managed a team of eight students in completing software tasks on time using agile development. Used the Robot Operating System, python and C++ to implement self-driving algorithms and simulations.}
    \resumeSubItem{Robojackets}
      {Designed and implemented a new defense strategy for Georgia Tech's autonomous robot soccer team.}
  \resumeSubHeadingListEnd
  
%-----------AWARDS-----------------
\section{Honors \& Awards}
  \resumeSubHeadingListStartBullets
    \resumeSubItem{Eagle Scout}
      {Achieved the rank of Eagle Scout through the Boy Scouts of America.}
  \resumeSubItem{Hyland Hackathon (First Place)}
      {Built an Android app that encourages exercise through a videogame.}  
  \resumeSubItem{Capital One SES Hackathon (Second Place)}
      {Built a webapp that predicts Lyft ride-sharing price surges..}      
  \resumeSubHeadingListEnd

%--------PROGRAMMING SKILLS------------
\section{Skills}
  \resumeSubHeadingListStart
    \resumeSubItem{Languages}
      {Python, Java, Javascript, C++, C, Scala, MATLAB}
    \resumeSubItem{Technologies}
      {Git, Node.js, React, MySQL, MongoDB, Elasticsearch, Flask, AWS, Docker, Linux, HTML/CSS}
  \resumeSubHeadingListEnd


%-------------------------------------------
\end{document}

"""


def latex_to_html(latex_code):
    with tempfile.NamedTemporaryFile(
        suffix=".tex"
    ) as texfile, tempfile.NamedTemporaryFile(suffix=".html") as htmlfile:

        texfile.write(latex_code.encode("utf-8"))
        texfile.flush()

        subprocess.run(
            [
                "pandoc",
                texfile.name,
                "--from=latex",
                "--to=html",
                "--mathjax",
                "-o",
                htmlfile.name,
            ],
            check=True,
        )

        return htmlfile.read().decode("utf-8")


from bs4 import BeautifulSoup


def latex_to_html_with_flex(latex_code):
    html_body = latex_to_html(latex_code)
    soup = BeautifulSoup(html_body, "html.parser")

    # Find all tables
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        wrapper = soup.new_tag("div", **{"class": "resume-subheading-wrapper"})

        for row in rows:
            tds = row.find_all("td")
            if len(tds) != 2:
                continue

            # create flex container for this row
            row_div = soup.new_tag("div", **{"class": "resume-subheading"})

            left = soup.new_tag("div", **{"class": "job-title"})
            # force the job title to italic instead of bold
            for content in tds[0].contents:
                if isinstance(content, str):
                    i_tag = soup.new_tag("i")
                    i_tag.string = content
                    left.append(i_tag)
                else:
                    left.append(content)

            right = soup.new_tag("div", **{"class": "company-location"})
            for content in tds[1].contents:
                right.append(content)

            row_div.append(left)
            row_div.append(right)

            wrapper.append(row_div)

        # Replace the table in the tree safely
        if table.parent:
            table.replace_with(wrapper)

    return str(soup)


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Interactive LaTeX Preview</title>

  <!-- Tailwind CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- MathJax -->
  <script>
    window.MathJax = {
      tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }
    };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
  
  <style>
/* Overall page styling to mimic PDF letter size */
body {
    background-color: #f3f4f6;
    font-family: "Times New Roman", serif;
    margin: 0;
    padding: 2rem;
}

.resume-container {
    max-width: 8.5in; /* standard letter width */
    margin: auto;
    background: white;
    padding: 1in; /* 1 inch margin like LaTeX */
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    line-height: 1.2;
}

/* Headings like LaTeX sections */
h1, h2, h3, h4, h5, h6 {
    margin: 0.5rem 0 0.25rem;
    font-weight: bold;
}

h1 { font-size: 24px; border-bottom: 1px solid black; padding-bottom: 4px; }
h2 { font-size: 20px; border-bottom: 1px solid #666; padding-bottom: 2px; }
h3 { font-size: 18px; }

/* Section formatting */
.section {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* Lists like resumeSubHeadingListStart / resumeItemListStart */
ul, ol {
    margin: 0.25rem 0 0.5rem 1.25rem;
    padding: 0;
}

li {
    margin-bottom: 0.25rem;
}

/* Subheadings (job / education) */

.resume-subheading-wrapper {
    margin-bottom: 0.5rem;
}

.resume-subheading {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.1rem;
}

.job-title {
    font-weight: normal;   /* remove bold */
    font-style: italic;    /* force italic */
}


.company-location {
    font-style: italic;
}

/* Skills and small text */
.small {
    font-size: 0.85rem;
}

/* Hyperlinks */
a {
    color: black;
    text-decoration: none;
}

/* Optional: checkbox overlay like your HTML preview */
.checkbox-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.25rem 0;
}

.checkbox-wrapper input[type="checkbox"] {
    margin-top: 0.25rem;
}

.checkbox-wrapper:hover {
    background-color: #f0f9ff;
}
</style>
 
</head>

<body class="bg-gray-100 p-10">
  <div class="max-w-4xl mx-auto bg-white shadow-lg p-10 rounded-lg">
 
    <!-- LaTeX Output -->
    <div id="latex-content" class="space-y-4">
      {{ content|safe }}
    </div>
  </div>

<script>
  // Wrap paragraphs with checkboxes
  document.querySelectorAll("#latex-content p").forEach((p, i) => {
    const wrapper = document.createElement("div");
    wrapper.className = "flex gap-3 items-start p-2 rounded hover:bg-gray-50";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "mt-1";

    checkbox.addEventListener("change", () => {
      wrapper.classList.toggle("bg-blue-50", checkbox.checked);
       if (checkbox.checked) {
    console.log(p.innerText.trim());
  }
    });

    wrapper.appendChild(checkbox);
    wrapper.appendChild(p.cloneNode(true));
    p.replaceWith(wrapper);
  });
</script>

</body>
</html>
"""


# @app.route("/")
# def index():
#     html_body = latex_to_html(LATEX_SOURCE)
#     return render_template_string(TEMPLATE, content=html_body)


@app.route("/")
def index():
    html_body = latex_to_html_with_flex(LATEX_SOURCE)
    return render_template_string(TEMPLATE, content=html_body)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
