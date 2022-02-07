import requests

r = requests.get("https://script.google.com/macros/s/AKfycbxim1y5h9u-SitfTC9JwlKDb3NOlRgmu3ZYczUWRc_JrT_H9DhLQeC3Hi9cFsLsCxsB9Q/exec", {
    "f": "find",
    "name": "Миша",
    "thing": "просто ответил долго",
    "points": 500
})
print(r.text)