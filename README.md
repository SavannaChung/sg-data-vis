# SG data vis
A project to develop a dashboard for Spot Grid data visualization, supporting interactive analysis of SpotPosition datasets.

## Project Overview
Phase 1 - perform exploratory data analysis on the spot position, size, symmetry data and identify suitable plots to present/trend the data.  
Phase 2 - design the layout of a user firendly, interactive dashboard, understad how to get info from the dashboard and write a callback function to refresh the graphs using plotly and dash packages.  
Phase 3 - build the dashboard.  

## Project structure
```
├── LICENSE                     <- Open-source license (if applicable)
├── README.md                   <- Project documentation
│
├── code/                       <- Source code
│   ├── database.py             <- Database access and query functions
│   ├── figure.py               <- Data visualization and plotting functions
│   └── main.py                 <- Entry point to run visualizations
│
├── data/                       <- Project datasets
│   └── xlsx_exported_from_access <- Excel export of SpotPositionResult table
│                              
│
├── docs/                       <- Documentation
│   ├── data_dictionaries/      <- Definitions of data parameters
│   │   └── data_dictionary.md
│   └── references/             <- Work instructions and reference docs
│       └── reference_docs.md
│
├── notebooks/                  <- Jupyter notebooks
│   └── eda_template.ipynb      <- Template for exploratory data analysis
│
├── requirements_32bit.txt      <- Dependencies for 32-bit Python
├── requirements_64bit.txt      <- Dependencies for 64-bit Python
└── references/                 <- Supplementary manuals and background materials


```
## Installation
1.) Clone the respository
```bash
git clone https://github.com/yourusername/SG-data-vis.git
cd sg-data-vis
```

2.) Set  up a virtual environment
```bash
python -m venv data_vis
source data_vis/bin/activate      # macOS / Linux (codespace is running in Linux)
# data_vis\Scripts\activate       # Windows (you may prefer to set up a virtual environment in conda if you are running in windows.)
```

3.) Install dependencies
- For a 32-bit environment
```bash
pip install -r requirements_32bit.txt
```
  
- For a 64-bit environment (ie. in codespace)
```bash
pip install -r requirements_64bit.txt
```


## Usage
Run the main script to generate plots in the sg-data-vis folder:
```bash
python code/main.py
```

## Contributing

1.) Fork the repository
2.) Create a feature branch 
```bash
git checkout -b feature-name
```
3.) Commit your changes 
```bash
git commit -m "Add new feature"
```
4.) Push to branch 
```bash
git push origin feature-name
```
5.) Open a Pull Request

## License

This project is licensed under the MIT License – see LICENSE
 for details.




