function getInputValue(id) {
  var inputValue = document.getElementById(id).value;
  return inputValue;
}

function ShowTable(id) {
  const column = ['id', 'nazev', 'rok', 'doba', 'obtiznost'];
  const query = `query{videohraAll{id,nazev,rok,doba,obtiznost}}`;
  //const query = `query{videohraAll{id,nazev,rok,doba,obtiznost,zanr{nazev}}}`;

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
        return data.data.videohraAll;
        //return data.data.videohraAll.map(object => [object.id, object.nazev, object.rok, object.doba, object.obtiznost, object.zanr.nazev]);
      },
    },
  }).render(document.getElementById(id));
}

function HttpRequest(resolver){
  var query;
  //var videohra_id = getInputValue("videohra_id");
  var videohra_nazev = getInputValue("videohra_nazev");
  var videohra_rok = getInputValue("videohra_rok");
  var videohra_doba = getInputValue("videohra_doba");
  var videohra_obtiznost = getInputValue("videohra_obtiznost");
  var videohra_odstran = getInputValue("videohra_odstran");

  switch(resolver){
    case "createVideohra":
      //query = `mutation{createVideohra(videohra:{id:${videohra_id},nazev:"${videohra_nazev}",rok:${videohra_rok},doba:"${videohra_doba}",obtiznost:"${videohra_obtiznost}"}){ok}}`;
      query = `mutation{createVideohra(videohra:{nazev:"${videohra_nazev}",rok:${videohra_rok},doba:"${videohra_doba}",obtiznost:"${videohra_obtiznost}"}){ok}}`;
      break;
    case "updateVideohra":
      query = `mutation{updateVideohra(videohra:{id:34,nazev:"hra"}){ok}}`;
      break;
    case "deleteVideohra":
      query = `mutation{deleteVideohra(videohra:{id:${videohra_odstran}}){ok}}`;
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

ShowTable("wrapper1")