// import { baseNodes, variants } from "graphData";
// import Fuse from "fuse";
// import { selectNode } from "graphControls";

const alphabet = [
  " ",
  "-",
  "ʿ",
  "a",
  "b",
  "c",
  "d",
  "e",
  "f",
  "g",
  "h",
  "ḫ",
  "i",
  "j",
  "k",
  "l",
  "m",
  "n",
  "o",
  "p",
  "q",
  "r",
  "s",
  "ṣ",
  "š",
  "t",
  "ṭ",
  "u",
  "v",
  "w",
  "x",
  "y",
  "z",
];

const orderedArray = baseNodes.map((node, i) => {
  const nameArray = [];
  for (const c of node.canonical_name.toLowerCase()) {
    const num = alphabet.indexOf(c);
    nameArray.push(num);
  }
  return { name: nameArray, index: i };
});

orderedArray.sort((a, b) => {
  let n = 0;
  let i = 0;

  const minLength = [a.name, b.name].reduce((min, current) => {
    if (current.length < min) {
      min = current.length;
    }
    return min;
  }, 50);

  while (n === 0 && i < minLength) {
    n = a.name[i] - b.name[i];
    i++;
  }
  return n;
});

const orderedNodes = orderedArray.map((x) => {
  return baseNodes[x.index];
});

function createUlElement() {
  const ulEle = document.getElementById("listOfNames");
  for (const node of orderedNodes) {
    const liEle = document.createElement("li");
    liEle.id = node.name_id;
    const a = document.createElement("a");
    a.onclick = () => {
      selectNode(node);
    };
    a.innerHTML = node.canonical_name;
    liEle.append(a);
    ulEle.append(liEle);
  }
}

// Fuse settings
const options = {
  isCaseSensitive: false,
  findAllMatches: false,
  includeMatches: false,
  includeScore: false,
  useExtendedSearch: false,
  minMatchCharLength: 1,
  shouldSort: true,
  threshold: 0.6,
  location: 0,
  distance: 100,
  keys: ["canonical_name", "variants"],
};

const fuse = new Fuse(variants, options);

function autocomplete(inp) {
  let currentFocus;
  inp.addEventListener("input", function (e) {
    let b;
    const val = this.value;
    closeAllLists();
    if (!val) {
      return false;
    }
    currentFocus = -1;
    const a = document.createElement("div");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    this.parentNode.appendChild(a);
    const matches = fuse.search(val);
    for (const match of matches) {
      b = document.createElement("div");
      b.innerHTML = match.item.variant;
      b.id = match.item.name_id;
      b.addEventListener("click", function (e) {
        // const selValue = this.id;
        const selValue = match.item.name_id;
        const node = baseNodes.find((x) => x.name_id === selValue);
        selectNode(node);
        closeAllLists();
      });

      a.appendChild(b);
    }
  });

  inp.addEventListener("keydown", function (e) {
    let x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode === 40) {
      currentFocus++;
      addActive(x);
    } else if (e.keyCode === 38) {
      currentFocus--;
      addActive(x);
    } else if (e.keyCode === 13) {
      e.preventDefault();
      if (currentFocus > -1) {
        if (x) x[currentFocus].click();
      }
    }
  });
  function addActive(x) {
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = x.length - 1;
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    for (let i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    const x = document.getElementsByClassName("autocomplete-items");
    for (let i = 0; i < x.length; i++) {
      if (elmnt !== x[i] && elmnt !== inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  document.addEventListener("click", function (e) {
    closeAllLists(e.target);
  });
}

// footer

const colls = document.getElementsByClassName("collapsible-footer");

for (let i = 0; i < colls.length; i++) {
  colls[i].addEventListener("click", () => {
    colls[i].classList.toggle("active");
    const content = colls[i].nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

createUlElement();
