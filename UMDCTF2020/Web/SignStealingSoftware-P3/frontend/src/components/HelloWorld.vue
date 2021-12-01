<template>
  <div class = "container">
    <div class = "row">
      <div class = "col-12">
        <h1>Houston Astro's Player Database</h1>
      </div>
    </div>
    <form v-on:submit.prevent="getTeamData(teamID, playerID)">
      <div class = "row">
        <div class = "col-5">
          <select class = 'form-control' v-model="teamID">
            <option :value="team" v-for="team in teams" v-bind:key="team">
              {{team}}
            </option>
          </select>
        </div>
        <div class = "col-5">
          <input type="text" class="form-control" v-model="playerID" placeholder="Player">
        </div>
        <div class = "col-2">
          <input type="submit" value="Submit" class = "btn btn-primary">
        </div>
      </div>
      <br>
    </form>
    <div class = "row">
      <div class = "col-12">
        <table class = "table">
          <thead class = "thead-dark">
            <th>Player</th>
            <th>Hits</th>
            <th>Walks</th>
            <th>Strike Outs</th>
          </thead>
          <tbody>
            <tr v-for="player in data" :key="player.playerID">
              <td> {{player.playerID}} </td>
              <td> {{player.H}} </td>
              <td> {{player.BB}} </td>
              <td> {{player.SO}} </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import * as axios from 'axios';

function getData(team, player) {
  return axios.post("http://159.89.228.183:5000/api/v1/resources/playerdata",
  {
    "team": team,
    "player": player
  }).then(response => {
    return response.data;
  }).catch(error=>{
    console.error(error);
  })
}
export default {
  name: 'HelloWorld',
  props: {
    msg: String,
  },
  created() {
    this.getTeamData("HOU", "all");
  },
  data() {
    return {
      teamID: "HOU",
      playerID: "all", 
      data: [],
      teams: ['ARI', 'ATL', 'BAL', 'BOS', 'CHA', 'CHN', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCA', 'LAA', 'LAN','TEX', 'MIA', 'MIL', 'MIN', 'NYN', 'NYY', 'OAK', 'PHI', 'PIT', 'SDN', 'SEA', 'SFN', 'SLN', 'TBA', 'TOR', 'WAS']
    }    
  },

  methods: {
    getTeamData(team, player){
      if (team !== "" && player !== "") {
        team = team.toString();
        player = player.toString();
        this.data = []
        getData(team, player).then(data => {
          if (data.length === 0) {
            alert("Player or team not found");
          } else {
            this.data = data;

          }
        }).catch((error) => {
          console.error(error);
        });
      } else {
        alert("Invalid input");
      }
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
