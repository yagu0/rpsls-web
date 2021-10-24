const socket = io();

const getV = (field) => localStorage.getItem(field);

const Login = {
  view: function() {
    return m("input[type=text][placeholder=User name]", {
      autofocus: true,
      onchange(e) {Login.username = e.currentTarget.value},
      onkeyup: Login.process
    });
  },
  process: function(e) {
    if (e.keyCode == 13) socket.emit("login", e.target.value);
  }
};

let Seek = {
  searching: false,
  seekGame: function() {
    // If not logged in, redirect
    if (!getV("name")) m.route.set("/login");
    else {
      socket.emit("seek", {uid: getV("uid"), name: getV("name")});
      Seek.searching = true;
    }
  },
  view: function(vnode) {
    if (Seek.searching)
      return m("img.animated", {src: "assets/searching.gif"});
    return m("button", {onclick: Seek.seekGame}, "Play");
  }
};

const Choices =
  {'r':"Rock",'p':"Paper",'s':"Scissors",'l':"Lizard",'k':"Spock",'?':"what"};
const Win =
  {'r':['s','l'], 'p':['r','k'], 's':['p','l'], 'l':['p','k'], 'k':['r','s']};
const MAX_POINTS = 7;

let Play = {
  gid: 0,
  mymove: "",
  oppmove: "",
  myselect: "?",
  oppselect: "?",
  mypoints: 0,
  oppoints: 0,
  mnum: 0,
  oppid: 0,
  oppname: "",
  gameover: false,
  initGame: function(msg) {
    Play.gid = msg.gid;
    Play.oppid = msg.oppid;
    Play.oppname = msg.oppname;
    Play.gameover = false;
    for (const v of ["mymove","oppmove"]) Play[v] = "";
    for (const v of ["myselect","oppselect"]) Play[v] = "?";
    for (const v of ["mnum","mypoints","oppoints"]) Play[v] = 0;
  },
  compareMoves: function() {
    Play.oppselect = Play.oppmove; //reveal opponent's move only now
    if (Win[Play.mymove].includes(Play.oppmove)) {
      if (++Play.mypoints == MAX_POINTS) Play.endGame(true);
    }
    else if (Win[Play.oppmove].includes(Play.mymove)) {
      if (++Play.oppoints == MAX_POINTS) Play.endGame(false);
    }
    Play.mnum++;
    Play.mymove = "";
    Play.oppmove = "";
  },
  endGame: function(Iwin) {
    Play.gameover = true;
    setTimeout(() => {
      if (Iwin) alert("Bravo t'as gagné !");
      else alert("Pas de chance, t'as perdu...");
      m.route.set("/seek");
    }, 1000);
  },
  playMove: function(code) {
    if (Play.mymove || Play.gameover)
      // I already played, or game is over
      return;
    Play.mymove = code;
    Play.myselect = code;
    socket.emit("move", {
      uid: getV("uid"),
      gid: Play.gid,
      choice: Play.mymove,
      mnum: Play.mnum,
      oppid: Play.oppid
    });
    if (Play.oppmove) Play.compareMoves();
    else Play.oppselect = "?";
  },
  view: function() {
    return m("div", {},
      [m("h2", {},
        `${getV("name")} [${Play.mypoints}] vs. ${Play.oppname} [${Play.oppoints}]`)]
      .concat(
      [m(".choices", {}, [
        m("img", {src: "assets/" + Choices[Play.myselect] + ".png"}),
        m("img", {src: "assets/" + Choices[Play.oppselect] + ".png"})
      ])]).concat(
      [m(".options",
        {style: `opacity:${Play.mymove==''?'1':'0.5'}`},
        ["r","p","s","l","k"].map((code) => {
        return m("img", {
          src: "assets/" + Choices[code] + ".png",
          onclick: () => Play.playMove(code)
        })
      }))])
    );
  }
};

socket.on("login", (msg) => {
  if (!msg.err) {
    localStorage.setItem("name", msg.name);
    localStorage.setItem("uid", msg.uid);
    m.route.set("/seek");
  }
  else alert(msg.err);
});
socket.on("play", (msg) => {
  Seek.searching = false;
  if (msg.oppid == getV("uid")) {
    alert("Cannot play against self!");
    m.redraw(); //TODO: because no DOM interaction... ?
  }
  else {
    Play.initGame(msg);
    m.route.set("/play");
  }
});
socket.on("move", (msg) => {
  Play.oppmove = msg.choice;
  Play.oppselect = "?"; //not showing opponent selection yet!
  if (Play.mymove) Play.compareMoves();
  else Play.myselect = "?";
  m.redraw(); //TODO... (because no DOM interactions)
});

m.route(document.body, "/seek", {
  "/seek": Seek,
  "/play": Play,
  "/login": Login
});
