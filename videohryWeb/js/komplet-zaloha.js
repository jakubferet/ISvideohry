function getInputValue(id) {
  var inputValue = document.getElementById(id).value;
  return inputValue;
}

function ClearTable() {
  var inputValue = document.getElementById("zanr_id");
  var resultTable = document.getElementById("wrapper2");
  inputValue.value = "";
  resultTable.innerHTML = "";
}

function ShowTable(id, resolver) {
  var column;
  var query;
  var zanr_id = getInputValue("zanr_id");
  var wrapper = document.getElementById(id);
  wrapper.innerHTML = "";

  switch(resolver){
    case "videohra":
    case "videohraAll":
      column = ['id', 'nazev', 'rok', 'doba', 'obtiznost'];
      query = `query{videohraAll{id,nazev,rok,doba,obtiznost}}`;
      //query = `query{videohraAll{id,nazev,rok,doba,obtiznost,zanr{nazev}}}`;
      break;
    case "vyvspol":
    case "vyvspolAll":
      column = ['id', 'nazev', 'zeme', 'pocet'];
      query = `query{vyvspolAll{id,nazev,zeme,pocet}}`;
      break;
    case "zanr":
    case "zanrAll":
      column = ['id', 'nazev'];
      query = `query{zanrAll{id,nazev}}`;
      break;
    case "zamereni":
      column = ['ID', 'název', 'země', 'počet', 'žánr'];
      query = `query{zanr(id:${zanr_id}){zamereni{vyvspol{id,nazev,zeme,pocet},zanr{nazev}}}}`;
      break;
  }

  const grid = new gridjs.Grid({
    pagination: {
      limit: 10
    },
    search: true,
    sort: true,
  
    columns: column,
  
    server: {
      url: "http://localhost:31102/gql/",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query
      }),
      then: data => {
        switch(resolver){
          case "videohraAll":
            return data.data.videohraAll;
            //return data.data.videohraAll.map(object => [object.id, object.nazev, object.rok, object.doba, object.obtiznost, object.zanr.nazev]);
          case "vyvspolAll":
            return data.data.vyvspolAll;
          case "zanrAll":
            return data.data.zanrAll;
          case "zamereni":
            return data.data.zanr.zamereni.map(object => [object.vyvspol.id, object.vyvspol.nazev, object.vyvspol.zeme, object.vyvspol.pocet, object.zanr.nazev]);
        }
      }
    },
  }).render(wrapper);
  
  if (resolver == "zamereni"){
    grid.forceRender();
  }
}


function HttpRequest(resolver){
  var query;
  //var videohra_id = getInputValue("videohra_id");
  var videohra_nazev = getInputValue("videohra_nazev");
  var videohra_rok = getInputValue("videohra_rok");
  var videohra_doba = getInputValue("videohra_doba");
  var videohra_obtiznost = getInputValue("videohra_obtiznost");
  var videohra_odstran = getInputValue("videohra_odstran");
  var vyvspol_nazev = getInputValue("vyvspol_nazev");
  var vyvspol_zeme = getInputValue("vyvspol_zeme");
  var vyvspol_pocet = getInputValue("vyvspol_pocet");
  var vyvspol_odstran = getInputValue("vyvspol_odstran");

  switch(resolver){
    case "createVideohra":
      //query = `mutation{createVideohra(videohra:{id:${videohra_id},nazev:"${videohra_nazev}",rok:${videohra_rok},doba:"${videohra_doba}",obtiznost:"${videohra_obtiznost}"}){ok}}`;
      query = `mutation{createVideohra(videohra:{nazev:"${videohra_nazev}",rok:${videohra_rok},doba:"${videohra_doba}",obtiznost:"${videohra_obtiznost}"}){ok}}`;
      break;
    case "createVyvspol":
      query = `mutation{createVyvspol(vyvspol:{nazev:"${vyvspol_nazev}",zeme:"${vyvspol_zeme}",pocet:${vyvspol_pocet}}){ok}}`;
      break;
    case "createZanr":
      query = `mutation{createZanr(zanr:{nazev:"zanr"}){ok}}`;
      break;
    case "updateVideohra":
      query = `mutation{updateVideohra(videohra:{id:34,nazev:"hra"}){ok}}`;
      break;
    case "updateVyvspol":
      query = `mutation{updateVyvspol(vyvspol:{id:19,nazev:"vyvspol"}){ok}}`;
      break;
    case "updateZanr":
      query = `mutation{updateZanr(zanr:{id:9,nazev:"zanr"}){ok}}`;
      break;
    case "deleteVideohra":
      query = `mutation{deleteVideohra(videohra:{id:${videohra_odstran}}){ok}}`;
      break;
    case "deleteVyvspol":
      query = `mutation{deleteVyvspol(vyvspol:{id:${vyvspol_odstran}}){ok}}`;
      break;
    case "deleteZanr":
      query = `mutation{deleteZanr(zanr:{id:9}){ok}}`;
      break;
  }
  fetch("http://localhost:31102/gql/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query
    }), 
  }).then(response => {
    return response.json();
  }).then(data => {
    console.log(data);
  });
}


ShowTable("wrapper1", "videohraAll")
ShowTable("wrapper1a", "vyvspolAll")