# SG data vis
A project to develop a dashboard for spot grid data visualisation

├── LICENSE               <- Open-source license if one is chosen
├── README.md             <- The top-level README for developers using this project
├── code                  <- The top-level README for developers using this project
│   ├── database.py       <- functions to interact with our database
│   ├── figure.py         <- data plotting functions
│   └── main.py           <- run this script to plot data
|
├── data
│   ├── access_backend                  <- has SpotPosition data only and this copy is decrypted for data visualisation training purposes
│   └── xlsx_exported_from_access       <- export "SpotPositionResult" table from Access database to an xlsx
│   
├── docs
│   ├── data_dictionaries           
│   |    └── data_dictionaries      <- define the parameters recorded in data folder
│   |
│   └── references                  
│        └── data_dictionaries      <- reference doc/work instruction related in this project
│
├── notebooks          
|       └── eda_template.ipynb      <- notebook template to explore different ways to present the data. 
│                     
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         scintillator_uniformity and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
│
├── requirements_32bit.txt   <- required packages when you set up a 32-bit env
│
└── requirements_64bit.txt   <- required packages when you set up a 64-bit env in codespace
