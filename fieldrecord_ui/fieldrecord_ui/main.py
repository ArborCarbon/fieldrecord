from distutils.log import debug 
from fileinput import filename
from flask import *
from flask import flash, render_template, request, redirect, url_for
import json 
import os 
from zipfile import ZipFile, ZIP_DEFLATED
from fieldrecord.__main__ import run_field_record
from fieldrecord.graphs_and_plots import run_graphs_and_plots
import shutil
import threading
import time
from io import BytesIO


app = Flask(__name__)  
app.secret_key = "secret key" 
UPLOAD_FOLDER = '/tmp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = '/tmp/output/'
app.config['FOLDER_NAME'] = 'output.zip'

def reset_output_folder():
    print("Resetting output folder")
    # Check if the OUTPUT_FOLDER exists
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        # Delete all files and subdirectories in the OUTPUT_FOLDER
        shutil.rmtree(app.config['OUTPUT_FOLDER'])
    # Recreate the OUTPUT_FOLDER directory
    os.makedirs(app.config['OUTPUT_FOLDER'])

def delete_output_folder():
    time.sleep(120)  # Wait for 2 minutes before deleting the folder

# Reset the OUTPUT_FOLDER when the program starts
reset_output_folder()

def clear_flash_messages():
    # Clear all flashed messages
    with app.test_request_context():
        flash("", "danger")
        flash("", "success")
        # Add more flash categories if needed
  
@app.route('/')   
def main():   
    clear_flash_messages()
    return render_template('index.html')

@app.route('/fieldrecord', methods = ['POST'])
def fieldrecord():
    clear_flash_messages()
    return render_template('fieldrecord.html')

@app.route('/generate_graphs', methods = ['POST'])
def generate_graphs():
    clear_flash_messages()
    return render_template('graphs_and_plots.html')
  
@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':   
        print("Posted")
        # get the zipped folder from the form
        f = request.files['file'] 
        # get the filenames from the form
        plantations_layer = request.form['plantations-layer']
        polygons_points = request.form['polygons-points-layer']
        abiotic_map_str = request.form.get('abiotic_map')
        pests_str = request.form.get('pests')
        severity_map_str = request.form.get('severity_map')
        severity_rank_str = request.form.get('severity_rank')
        columns_str = request.form.get('columns')

        abiotic_map = json.loads(abiotic_map_str)
        severity_map = json.loads(severity_map_str)
        severity_rank = json.loads(severity_rank_str)
        pests = json.loads(pests_str)
        columns = json.loads(columns_str)

        pest_map = {x: x for x in pests}
        

        print(f.filename, plantations_layer, polygons_points)
        print("Requested")
        if not f.filename.endswith('.zip'):
            flash('Uploaded file must be a zip file', 'danger')
            return redirect(url_for('main'))
        path = os.path.join(app.config['UPLOAD_FOLDER'],f.filename)
        f.save(path)  
        print("Saved")

        # only the name of the uploaded folder, without the .zip extenstion 
        folder_name = os.path.splitext(f.filename)[0]
        app.config['FOLDER_NAME'] = folder_name

        plantations_path = os.path.join(folder_name, plantations_layer)
        manual_path = os.path.join(folder_name, polygons_points)

        with ZipFile(path, 'r') as zObject:
            zObject.extractall(app.config['UPLOAD_FOLDER'])
            print("extracted files: ", zObject.namelist())
            if plantations_path not in zObject.namelist():
                print("Invalid filename: ", plantations_path)
                flash('Plantations layer filename must match the name of a provided file', 'danger')
                return redirect(url_for('main'))
            if manual_path not in zObject.namelist():
                print("Invalid filename: ", polygons_points)
                flash('Polygons/points filename must match the name of a provided file', 'danger')
                return redirect(url_for('main'))
            print("Extracted")

            plantations_path2 = os.path.join(app.config['UPLOAD_FOLDER'], plantations_path)
            manual_path2 = os.path.join(app.config['UPLOAD_FOLDER'], manual_path)


            if not os.path.exists(app.config['OUTPUT_FOLDER']):
                os.makedirs(app.config['OUTPUT_FOLDER'])

            # output_path = Path("/home/arborcarbon/BigFella/Development/IR/test")

            run_field_record(plantation_path=plantations_path2, manual_path=manual_path2, out_dir=app.config['OUTPUT_FOLDER'], abiotic_map=abiotic_map, pest_map=pest_map, severity_map=severity_map, severity_rank=severity_rank, columns_to_process=columns)

        return render_template("download.html", name=f.filename)   
    

@app.route('/download')
def download():
    # Print the contents of the output folder
    print(os.listdir(app.config['OUTPUT_FOLDER']))

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, 'w', compression=ZIP_DEFLATED, compresslevel=9, allowZip64=True) as zip_file:
        for root, dirs, files in os.walk(app.config['OUTPUT_FOLDER']):
            for file in files:
                if file not in ['output.zip', 'point_obs.gpkg', 'plantations.gpkg', 'polygon_obs.gpkg']:
                    zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), app.config['OUTPUT_FOLDER']))
                    print(f"Added {file} to zip buffer")

    zip_buffer.seek(0)

    # Check if the ZIP buffer has content
    if zip_buffer.getbuffer().nbytes == 0:
        flash("Failed to create ZIP file", "danger")
        return redirect(url_for('main'))

    download_name = f"{app.config['FOLDER_NAME']}_processed.zip"

    return send_file(zip_buffer, as_attachment=True, download_name=download_name, mimetype='application/zip')

    

    
    # return redirect(url_for('main'))


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.zip'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            filenames = zip_ref.namelist()

        os.remove(filepath)
        return jsonify({'filenames': filenames})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload_graphs', methods=['POST'])
def upload_graphs():

    # Retrieve the form data
    region_col = request.form['region_col']
    district_col = request.form['district_col']
    code_col = request.form['code_col']
    area_col = request.form['area_col']
    year = request.form['year']
    
    pest_area_file = request.files['pest_area_file']
    final_pest_area_file = request.files['final_pest_area_file']

    # Save the files
    pest_area_path = os.path.join(app.config['UPLOAD_FOLDER'], pest_area_file.filename)
    final_pest_area_path = os.path.join(app.config['UPLOAD_FOLDER'], final_pest_area_file.filename)
    
    pest_area_file.save(pest_area_path)
    final_pest_area_file.save(final_pest_area_path)

    # Call the run_graphs_and_plots function with the provided data
    outdir = app.config['OUTPUT_FOLDER']
    run_graphs_and_plots(outdir, region_col, district_col, code_col, area_col, year, pest_area_path, final_pest_area_path)

    return render_template("download.html", name="output.zip") 
  
if __name__ == '__main__':   
    # app.run(debug=True)
    app.run(host='192.168.0.202', port=8080, debug=True)