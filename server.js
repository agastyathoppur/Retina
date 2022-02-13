const express = require('express');
const app = express();
const cors = require('cors');
const port = 2000;
app.use(cors())

var MongoClient = require('mongodb').MongoClient;
var url = "mongodb://localhost:27017/";

MongoClient.connect(url, function(err, db) {
    if (err) throw err;

    var dbo = db.db("BlinksDatabase");
    var blinkData = {}
    dbo.collection("Blinkstats").find().toArray(function(err, result) {
        if (err) throw err;

        result.forEach((item) => {
                if (blinkData[item.Date] !== undefined) {
                    blinkData[item.Date][item.Time] = [parseInt(item.BlinkRate), item.DrynessLevel]
                } else {
                    blinkData[item.Date] = {}
                }
            })
        app.get('/', (req, res) => {
            res.json(blinkData)
        })

        app.listen(port, () => {
            console.log(`Example app listening on port ${port}`)
        })
        db.close();
    });
});
