console.log("starting")
var express = require("express");
const Cors = require("cors");
var app = express();
app.use(Cors());
const dotenv = require("dotenv");
//process.env.DB_USERNAME
dotenv.config();

  app.get("/hi", (req, res) => {
    console.log("query1");
    
  });

  app.get("/login", (req, res) => {
    // console.log(req, "query *");
    print("req",req)
    res.send("hello");
  });
  app.listen(5000, function () {
    console.log("Example app listening on port 5000!");
  });
