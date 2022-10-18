import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask, render_template, request, flash, url_for, redirect, send_from_directory, send_file
import pandas as pd
import csv
import mplstereonet
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import glob
import os
import matplotlib.pyplot as plt
import random
import shutil
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/files/"
app.config['SECRET_KEY'] = 'supersecretkey'
full_path = os.path.join(app.root_path, 'static/')

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# INDEX
@app.route("/", methods=['GET','POST'])
def index():

    title = "Home"
    form = UploadFileForm()


    if form.validate_on_submit():
        if os.path.exists('static/Stereoplots.zip'):
            os.remove('static/Stereoplots.zip')
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) 
        
        data_dir = os.path.dirname("static/files/")
        
        data = pd.read_csv('static/files/data.csv')
        data['Colour']='0'

        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111, projection='stereonet')
        for i in range(len(data)):
                if data.loc[i][2].upper() == 'BEDDING':
                        data['Colour'][i]='k'
                elif data.loc[i][2].upper() == 'CLEAVAGE':
                        data['Colour'][i]='g'
                elif data.loc[i][2].upper() == 'FAULT':
                        data['Colour'][i]='r'

                chosen=data.loc[i][3]
                colour=chosen
                ax.plane(data.loc[i][0], data.loc[i][1], c=colour, label=data.loc[i][2].title() + ' %03d/%02d' % (data.loc[i][0], data.loc[i][1],), linewidth=2)
        ax.legend(loc='best')

        ax.grid()

        fig_dir = os.path.join(data_dir, 'Figures/')
        if not os.path.isdir(fig_dir):
            os.makedirs(fig_dir)

        png = "Stereoplot" + ".png"
        svg = "Editable_Plot" + ".svg"
        fig.savefig(fig_dir + png, bbox_inches='tight', dpi=300)
        fig.savefig(fig_dir + svg, bbox_inches='tight', dpi=300)

        bin_edges = np.arange(-5, 366, 10)

        strikes = data['strike']
        dips = data['dip']

        number_of_strikes, bin_edges = np.histogram(strikes, bin_edges)

        number_of_strikes[0] += number_of_strikes[-1]

        half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
        two_halves = np.concatenate([half, half])

        fig2 = plt.figure(figsize=(16,8))

        ax2 = fig2.add_subplot(121, projection='stereonet')

        vals = np.linspace(0,1,256)
        np.random.shuffle(vals)
        colours = ['viridis', 'plasma', 'Purples', 'Blues', 'Greens', 'Reds', 'Oranges', 'YlOrRd']
        cmaprose = random.choice(colours)
        r = random.random()
        b = random.random()
        g = random.random()
        rosecol = (r, g, b)

        ax2.pole(strikes, dips, c='k', label='Pole of the Planes')
        ax2.density_contourf(strikes, dips, measurement='poles', cmap=cmaprose)
        ax2.set_title('Density contour of the Poles', y=1.10, fontsize=20)
        ax2.grid()

        ax2 = fig2.add_subplot(122, projection='polar')

        ax2.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, 
            width=np.deg2rad(10), bottom=0.0, color=rosecol, edgecolor='k')
        ax2.set_theta_zero_location('N')
        ax2.set_theta_direction(-1)
        ax2.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
        ax2.set_rgrids(np.arange(1, two_halves.max() + 1, 2), angle=0, weight= 'black')
        ax2.set_title('Rose Diagram"', y=1.10, fontsize=20)

        fig2.tight_layout()
        png2 = "RoseDiagram" + ".png"
        svg2 = "Editable_Rose" + ".svg"
        fig2.savefig(fig_dir + png2, bbox_inches='tight', dpi=300)
        fig2.savefig(fig_dir + svg2, bbox_inches='tight', dpi=300)
        shutil.make_archive('static/Stereoplots', 'zip', 'static/files/figures')
        shutil.rmtree('static/files/figures')
        os.remove('static/files/data.csv')
        return send_from_directory(full_path,'Stereoplots.zip')

    return render_template('index.html', form=form)






@app.route('/plot', methods=['GET','POST'])

def plot_png():
    strike1, dip1 = 10, 30
    strike2, dip2 = 315, 78
    strike3, dip3 = 270, 50

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='stereonet')
    ax.plane(strike1, dip1, c='b', label='Bedding %03d/%02d' % (strike1, dip1))
    ax.plane(strike2, dip2, c='r', label='Fault %03d/%02d' % (strike2, dip2))
    ax.plane(strike3, dip3, c='g', label='Fault %03d/%02d' % (strike3, dip3))
    ax.legend()

    plunge, bearing = mplstereonet.plane_intersection(strike1, dip1, strike2, dip2)
    ax.line(plunge, bearing, 'ko', markersize=5, 
            label='Intersection %02d/%03d' % (plunge, bearing))
    ax.legend()
        # We can also add a grid
    ax.grid()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


if __name__ == '__app__':
    app.run(debug=True)



# Run the app in powershell
# $env:FLASK_APP = "app.py"
# $env:FLASK_DEBUG = "1"
# flask run 

# For pushing to github
# git add -A
# git commit -m "some text"
# git push


