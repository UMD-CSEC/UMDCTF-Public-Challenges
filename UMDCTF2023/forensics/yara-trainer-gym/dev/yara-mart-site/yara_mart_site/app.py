from flask import Flask, request, jsonify, render_template_string, render_template
import yara
import random
import json 
app = Flask(__name__)

# Define the HTML template
html_template = """
<!DOCTYPE html>
<html>
  <head>
    <title>YARA Gym</title>
    <style>
      /* Style for the match spaces */
      .match {
        display: inline-block;
        width: 100px;
        height: 100px;
        background-color: gray;
        margin: 5px;
        text-align: center;
        line-height: 100px;
        font-size: 24px;
      }
    </style>
  </head>
  <body>
    <h1>YARA Scan</h1>
    <form method="post" enctype="multipart/form-data">
      <label for="file">Select a file:</label>
      <input type="file" id="file" name="file"><br><br>
      <input type="submit" value="Scan">
    </form>
    <div id="matches">
      <!-- Eight match spaces -->
      {% for _ in range(8) %}
        <div class="match"></div>
      {% endfor %}
    </div>

    <script>
      const form = document.querySelector('form');
      const matches = document.querySelectorAll('.match');

      form.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(form);

        fetch('/', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          // display the matches in the spaces
          data.matches.forEach((match, index) => {
            matches[index].textContent = match;
          });
        })
        .catch(error => console.error(error));
      });
    </script>
  </body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if file is present in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file present'})

        # get the file from the request
        file = request.files['file']

        # read the YARA rules from a file
        with open('yara_rules.yar', 'r') as f:
            rules = yara.compile(file=f)

        # scan the file with the YARA rules
        matches = rules.match(data=file.read())

        gym_data = [
            {
              "image": "/static/roark.png",
              "name": "Roark",
              "rule": "rule1",
              "description": "Locked in a battle with Roark"
            },
            {
              "image": "/static/gardenia.png",
              "name": "Gardenia",
              "rule": "rule2",
              "description": "Locked in a battle with Gardenia"
            },
            {
              "image": "/static/fantina.png",
              "name": "Fantina",
              "rule": "rule3",
              "description": "Locked in a battle with Fantina"
            },
            {
              "image": "/static/maylene.png",
              "name": "Maylene",
              "rule": "rule4",
              "description": "Locked in a battle with Maylene"
            },
            {
              "image": "/static/crasher-wake.png",
              "name": "Crasher Wake",
              "rule": "rule5",
              "description": "Locked in a battle with Crasher Wake"
            },
            {
              "image": "/static/byron.png",
              "name": "Byron",
              "rule": "rule6",
              "description": "Locked in a battle with Byron"
            },
            {
              "image": "/static/candice.png",
              "name": "Candice",
              "rule": "rule7",
              "description": "Locked in a battle with Candice"
            },
            {
              "image":"/static/volkner.png",
              "name": "Volkner",
              "rule": "rule8",
              "description": "Locked in a battle with Volkner"
            }
        ]
        # return the results as JSON
        print([str(match) for match in matches])
        words = ["annihilated", "obliterated", "demolished", "devastated", "decimated", "crushed"]
        for i in gym_data:
            if i['rule'] in [str(match) for match in matches]:
                i['description'] = f"Your {request.files['file'].filename} defeated {i['name']}\'s {i['rule']} move!"
                i["background"] = "rgba(0, 128, 0, 0.5)"
            else:
                i['description'] = f"{i['name']}'s {i['rule']} {random.choice(words)} you!"
                i["background"] = "rgba(249, 68, 68, 0.5)"

        print(json.dumps({'matches': gym_data}))
        #print({'matches': [i["description"] = str(j) for i, j in zip(gym_data, [str(match) for match in matches])]})
        if len(matches) == 8:
            flag = "UMDCTF{Y0ur3_4_r34l_y4r4_m4573r!}"
        else:
            flag = ""
        return jsonify({'matches': gym_data, 'flag':flag})
        
    
    # if the request is a GET request, render the HTML template
    else:
        return render_template("index.html")#render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

