Book Now or Wait?  -  MS&E 152 final project, code and model files
Benjamin Solomon, Dias, Eugenio, Hamilton Sharpe

Everything in the report is generated from these files. Nothing is typed into
the document by hand, so a change to a source propagates everywhere it appears.


HOW TO REPRODUCE EVERY NUMBER
-----------------------------
Run in this order, from this folder, with Python 3.11. Every script resolves
its own paths relative to itself, so the folder can sit anywhere and can also
be run from another working directory.

    python3 analyse.py            rolls back all twelve rounds, writes
                                  model_results.json. Reads the group workbook,
                                  MSE_July_28_stayhome_fix.xlsx, from this
                                  folder.
    python3 build_genie_cdn.py    writes BookNowOrWait_CDN.xdsl from the same
                                  constants. Needs model_results.json.
    python3 build_nb_data.py      writes advance_data.csv, the 108-row file the
                                  course naive-Bayes tool is run on, and
                                  advance_data_audit.csv, the traceable copy
                                  hindsight.py reads.
    python3 check_genie_cdn.py    reads the .xdsl back with an independent
                                  parser, re-solves it, computes the three
                                  information regimes, enumerates rounds 4 to 6
                                  exactly, and runs 400,000 simulated
                                  tournaments. Writes verifier_output.txt.
                                  Takes about a minute.
    python3 hindsight.py          Brier-scores the forecast and replays each
                                  fixed strategy along both bracket paths.
                                  Needs advance_data_audit.csv from
                                  build_nb_data.py. Writes hindsight_output.txt.
    python3 sensitivity_v_scaling.py
                                  re-solves all twelve rounds under five ways the
                                  value of attending might vary with the round.
                                  Needs model_results.json. Writes
                                  sensitivity_output.txt.

The tornado diagrams are produced separately and depend on nothing above:

    python3 run_tornado.py        drives the course tornado generator with
                                  fifa_tornado_inputs.csv and fifa_utility.py

Requires numpy, pandas, openpyxl, matplotlib and bokeh.

    pip install numpy pandas openpyxl matplotlib bokeh

Running all seven in the order above reproduces every number in the report, and
the transcripts shipped here (verifier_output.txt, hindsight_output.txt,
sensitivity_output.txt) are the output of exactly that sequence.


WHAT EACH FILE IS
-----------------
inputs.py               Every sourced constant in one place: the advancement
                        probabilities, the value of attending, the price band,
                        the measured sensitivity and specificity. Nothing else
                        in the project hard-codes a number.

analyse.py              The solver. Applies each team's own advancement chain
                        and rolls back all twelve rounds.

build_genie_cdn.py      Writes the GeNIe network file from the same constants.

check_genie_cdn.py      The verification suite. Parses the .xdsl independently,
                        re-solves it, and runs every test reported in section 7.

build_nb_data.py        Builds the 108-row file the course naive-Bayes tool is
                        run on, which is where 0.8194 and 0.6607 come from.
                        Writes advance_data.csv and advance_data_audit.csv.

sensitivity_v_scaling.py
                        Section 4's test of the flat value of attending. Rebuilds
                        the twelve rounds under a v that scales with the round,
                        five ways, and reports which recommendations move.
                        Writes sensitivity_output.txt.

MSE_July_28_stayhome_fix.xlsx
                        The group workbook. analyse.py reads its A3_Inputs sheet
                        for the twelve rows of bundle prices. The Validation tab
                        is the independent spreadsheet implementation of the
                        Final round.

hindsight.py            Section 8's hindsight subsection only. Uses realised
                        results; feeds nothing back into the model.

fifa_tornado_inputs.csv The eight uncertain inputs with their 10th, 50th and
                        90th percentiles, in the format the course tornado
                        generator reads.

fifa_utility.py         The utility function the tornado is drawn against. At
                        every input's median it reproduces the Final-round
                        figures in the report to the cent. Run it directly to
                        see that check:  python3 fifa_utility.py

run_tornado.py          Drives the generator with the two files above.

tornado.py              The course tornado generator, by J. M. Agosta,
                        3 August 2026. Used unmodified and included so the
                        driver runs out of the box.

BookNowOrWait_CDN.xdsl  The causal decision network. Opens in GeNIe.
                        54 nodes: 30 chance, 12 decision, 12 utility.

BookNowOrWait_one_round_CDN.xdsl
                        The same network cut down to one generic round, which is
                        the view drawn as Figure 4 in the report. 11 nodes. Every
                        table and arc is taken straight out of the file above, so
                        the two cannot disagree; the only change is that the
                        previous round's node becomes a root carrying its
                        marginal, 0.4982 / 0.5018, because its parent is outside
                        the slice. This is a detail view, not a second model.

verifier_output.txt     Transcript of check_genie_cdn.py. Ends with
                        "all checks passed".

hindsight_output.txt    Transcript of hindsight.py.

sensitivity_output.txt  Transcript of sensitivity_v_scaling.py.

advance_data.csv        The 108-row naive-Bayes training set.
advance_data_audit.csv  The same rows with team, FIFA rank and the probability
                        that produced each signal, so every row is traceable.

model_results.json      The rolled-back result for all twelve rounds.
pack_extras.json        The derived figures the report quotes.
