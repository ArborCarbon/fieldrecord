# Forest-Health-Field-Record

## Run Guide 

The process for running the code has recently become a little convoluted, so soon I (IR) will update it. 

First you need to tidy up the ACSketch output just a little bit. I usually just read the file with errors='coerce', change the 'classification' column to be called 'CODE', and then save it to a .gpkg or a .geojson (the code does not recognise the current .geojson.json format).

Then I run 
```bash
cd /home/arborcarbon/BigFella/Development/IR/Forest-Health-Tools
uv run app/main.py
```

Then I open the website (this is just the easiest way to run the code really, at this stage it rarely fails), and I input the plantation layer (from Dave), the recently saved file, and dusually ticck the summary box and provide those cols (you might have to wait for it to load for a minute). 
Then press run. 
THere is no visual hint to indicate that the code is actually running except in the terminal (another dev job but it works so I haven't gotten around to this). And then hopefully when it's done it will auto-download the zip file with the outputs.