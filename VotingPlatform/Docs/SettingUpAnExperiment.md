# First time setup
Export the MBLab variables from Blender.
See panel: Export MBLab Attribute button.
Save the variables as csv. E.g.:
 `mblab_attributes-1_6_1.csv`.

 ![Characters Generation Tools Panel](Pics/GenerationToolsPanel.png "Characters Generation Tools")


Import the variables from Blender/MBLab.
Use: http://localhost:8000/admin/experiments/variable/
Click on `Import Variables`

# Create a new experiment

# Create two variable set

# Add variables to the set
It means adding entries in the variable range table.


# Create individuals for the experiment

![VotingPlatform-GenerationPanel](Pics/VotingPlatform-GenerationPanel.png "Voting Platform: Generation panel")


* Download the independent (physical attributes) variable set.
  - It creates a csv with variable ID, name, min, max, ...?
  - E.g.: `VS-1-testvarset1.csv`
* Use the generation subpanel to create a table of individuals.
  - Select the variables/attributes table.
  - Insert the number of individuals to create.
  - Insert the number of segments for the randomization. Useful to avoid very close values.
  - Values will be random in the provided range for each variable.
* Click the `Generate Individuals` button.
  - It creates a CSV file with each line: empty ID, for each attribute the value.
  - This is the format needed by the voting platform to import the individuals.
* Upload the generated individuals table in the Voting platform as Generation.
  - e.g. `http://localhost:8000/admin/experiments/generation/1/change/`: Create: Create or update individuals from file.
* Re-download the generation to have IDs.
  - Export: ExportIndividualsData
  - e.g. `GEN-1-gen1.csv`
* Convert the CSV in the json files needed to generate the pictures.
  - Select the variables table CVS files
  - Select the freshly crated individuals file.
  - Select an output directory
  - Click `Convert individuals` to MBLAB/JSON dir.
  - This will filla directory with JSON files, one for each individual.

# Create the pictures of the Individuals

![PicturesGenerationPanel](Pics/PicturesGenerationPanel.png "Pictures Generation Panel")

* Select the directory where you save your individuals' JSON files.
* Click `Load Scripts` button.
* Choose to save either head and/or body picture.
* Select the output path
* Select the resolution
* Render either the currently selected character or all of them.

# Upload the Pictures
