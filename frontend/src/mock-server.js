const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors())

app.get("/api/analysis", (req, res) => {
  res.json({
 "game_record_hd_id": "20260115-f3072931-6f6e-4d14-91a8-024ed3f8afce",
 "user_id": "mini13",
 "dominant_hand": "right",
 "shooting_result": [
    {"nth":1,"score":10.9,"time":0.7,"pointX":0.49414329361941167,"pointY":0.4970505136396491,"zoom":{"pointX":0.48469381777846243,"pointY":0.49229167850362077},"direction":"C","distance":2077,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":2,"score":10.4,"time":4.1,"pointX":0.5320780469193244,"pointY":0.5191507237373156,"zoom":{"pointX":0.5838342234614274,"pointY":0.5500493704395393},"direction":"SE","distance":2076,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":3,"score":8.9,"time":3.9,"pointX":0.4879082898618762,"pointY":0.6030441271608996,"zoom":{"pointX":0.4683989760255755,"pointY":0.7693001978742839},"direction":"S","distance":2077,"perfect":false,"distanceDisqualified":false,"color":"orange","timeOver":false},
    {"nth":4,"score":9.9,"time":3.9,"pointX":0.4833402442207222,"pointY":0.5511604174327769,"zoom":{"pointX":0.45646063825751765,"pointY":0.6337049564839798},"direction":"S","distance":2076,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":5,"score":9.9,"time":3.9,"pointX":0.5371589456005494,"pointY":0.5351867698211772,"zoom":{"pointX":0.5971128746367301,"pointY":0.5919587009612277},"direction":"SE","distance":2074,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":6,"score":8.5,"time":5,"pointX":0.5728343761095591,"pointY":0.6034779208925862,"zoom":{"pointX":0.690348663614058,"pointY":0.7704338940974312},"direction":"SE","distance":2072,"perfect":false,"distanceDisqualified":false,"color":"orange","timeOver":false},
    {"nth":7,"score":9.8,"time":4.9,"pointX":0.5551110793378805,"pointY":0.4830583547577994,"zoom":{"pointX":0.6440297955805112,"pointY":0.4557239355434926},"direction":"E","distance":2081,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":8,"score":10.1,"time":5.3,"pointX":0.517350513040719,"pointY":0.45779421751039256,"zoom":{"pointX":0.5453446181148204,"pointY":0.38969749282127797},"direction":"N","distance":2083,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":9,"score":9,"time":5.3,"pointX":0.5574170092557659,"pointY":0.577186374881575,"zoom":{"pointX":0.6500562174667496,"pointY":0.7017223746905026},"direction":"SE","distance":2082,"perfect":false,"distanceDisqualified":false,"color":"red","timeOver":false},
    {"nth":10,"score":8.9,"time":5.3,"pointX":0.5156419447382457,"pointY":0.6024355801121221,"zoom":{"pointX":0.5408793681814655,"pointY":0.7677097934022685},"direction":"S","distance":2080,"perfect":false,"distanceDisqualified":false,"color":"orange","timeOver":false}
 ],
 "coi": [0.5736, 0.4869],
 "mean_radius": 0.0345,
 "std": [0.0231, 0.1563],
 "ttf": 6.34,
 "skill_level": "beginner",
 "error_probabilities": {
   "jerking": 0.13,
   "loose_grip": 0.22,
   "heeling": 0.65,
  },
 "major_error": [
    {"error": "heeling", "confidence": 0.65},
    {"error": "Thumbing", "confidence": 0.45}
 ],
 "recommended_drill": "grip_basic"
  });
});

app.listen(4000, () => {
  console.log("Mock API running on http://localhost:4000");
});
