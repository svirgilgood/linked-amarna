// import { baseNodes, baseLinks } from "graphData";
// import * as d3 from "d3js";

const width = window.innerWidth;
const height = window.innerHeight;
const r = 6;

const nodes = [...baseNodes];
let links = [...baseLinks];

const fof = document.getElementById("fof-toggle");

const svg = d3.select("svg").attr("width", width).attr("height", height);

let linkElements, nodeElements, textElements;

let selectedId;

const linkGroup = svg.append("g").attr("class", "links");
const nodeGroup = svg.append("g").attr("class", "nodes");
const textGroup = svg.append("g").attr("class", "texts");

const linkForce = d3
  .forceLink() // ('link', d3.forceLink()
  .id((link) => {
    return link.name_id;
  })
  .distance(200)
  .strength(1);

const simulation = d3
  .forceSimulation()
  .force("link", linkForce)
  .force("charge", d3.forceManyBody().strength(-120))
  .force("center", d3.forceCenter(width / 2, height / 2));

const dragDrop = d3
  .drag()
  .on("start", (node) => {
    node.fx = node.x;
    node.fy = node.y;
  })
  .on("drag", (node) => {
    simulation.alphaTarget(0.7).restart();
    node.fx = d3.event.x;
    node.fy = d3.event.y;
  })
  .on("end", (node) => {
    if (!d3.event.active) {
      simulation.alphaTarget(0);
    }
    node.fx = null;
    node.fy = null;
  });

const languageObject = {
  Akkadian: { highlighted: "darkblue", normal: "powderblue" },
  Anatolian: { highlighted: "darkred", normal: "lightred" },
  Unknown: { highlighted: "black", normal: "grey" },
  Egyptian: { highlighted: "darkgoldenrod", normal: "lightgoldenrodyellow" },
  Hurrian: { highlighted: "rebeccapurple", normal: "plum" },
  WS: { highlighted: "darkgreen", normal: "lightgreen" },
  "Indo-Iranian": { highlighted: "orange", normal: "lightsalmon" },
};

function getNodeColor(node, neighbors) {
  if (neighbors.indexOf(node.name_id)) {
    return languageObject[node.language].highlighted;
  }
  return languageObject[node.language].normal;
}

function getNeighbors(node) {
  return baseLinks.reduce(
    (neighbors, link) => {
      if (link.target.name_id === node.name_id) {
        neighbors.push(link.source.name_id);
      } else if (link.source.name_id === node.name_id) {
        neighbors.push(link.target.name_id);
      }
      return neighbors;
    },
    [node.name_id]
  );
}

function getNodeSize(node) {
  if (node.hits < 10) {
    return 5;
  }
  if (node.hits >= 10 && node.hits <= 30) {
    return 10;
  }
  if (node.hits > 30) {
    return 15;
  }
}

function getTextColor(node, neighbors) {
  return Array.isArray(neighbors) && neighbors.indexOf(node.name_id) > -1
    ? "red"
    : "grey";
}

function getLinkColor(node, link) {
  return isNeighborLink(node, link) ? "green" : "#E5E5E5";
}

function isNeighborLink(node, link) {
  return (
    link.target.name_id === node.name_id || link.source.name_id === node.name_id
  );
}

function updateInfoBox(node) {
  const { language, canonical_name, scope_note, variants, occurances } = node;
  const heading = document.getElementById("select-node-info");
  heading.classList.toggle("active");
  heading.innerHTML = canonical_name;
  const content = heading.nextElementSibling;
  const langP = document.createElement("p");
  langP.innerHTML = `<b>Language:</b> ${language}`;
  const scopeP = document.createElement("p");
  scopeP.innerHTML = `<b>Scope Note:</b> ${scope_note}`;
  const variantP = document.createElement("p");
  const varString = variants.join(", ");
  variantP.innerHTML = `<b>Variants:</b> ${varString}`;
  const occurancesP = document.createElement("p");
  const occuranceString = occurances.join(", ");
  occurancesP.innerHTML = `<b>Occrances:</b> ${occuranceString}`;
  for (const ele of [scopeP, langP, variantP, occurancesP]) {
    content.appendChild(ele);
  }
}

function cleanInfoBox() {
  const heading = document.getElementById("select-node-info");
  heading.innerHTML = null;
  const content = heading.nextElementSibling;
  while (content.hasChildNodes()) {
    content.removeChild(content.firstChild);
  }
}

function selectNode(selectedNode) {
  if (selectedId === selectedNode.name_id) {
    selectedId = undefined;
    resetData();
    updateSimulation();
    cleanInfoBox();
  } else {
    cleanInfoBox();
    selectedId = selectedNode.name_id;
    updateData(selectedNode);
    updateSimulation();
    updateInfoBox(selectedNode);
  }
  const neighbors = getNeighbors(selectedNode);
  nodeElements.attr("fill", (node) => getNodeColor(node, neighbors));
  textElements.attr("fill", (node) => getTextColor(node, neighbors));
  linkElements.attr("stroke", (link) => getLinkColor(selectedNode, link));
}

function resetData() {
  const nodeIds = nodes.map((node) => {
    return node.name_id;
  });

  baseNodes.forEach((node) => {
    if (nodeIds.indexOf(node.name_id) === -1) {
      nodes.push(node);
    }
  });

  links = baseLinks;
}

function friendOfFriends(neighbors) {
  const extendedNeighbors = [];
  for (const neighbor of neighbors) {
    const neighborNode = baseNodes.find((x) => x.name_id === neighbor);
    const fof = getNeighbors(neighborNode);
    extendedNeighbors.push(...fof);
  }
  return extendedNeighbors;
}

function updateData(selectedNode) {
  const fof = document.getElementById("fof-toggle");
  let neighbors = getNeighbors(selectedNode);
  links = baseLinks.filter((link) => {
    if (fof.checked) {
      return (
        neighbors.includes(link.target.name_id) ||
        neighbors.includes(link.source.name_id)
      );
    }
    return (
      neighbors.includes(link.target.name_id) &&
      neighbors.includes(link.source.name_id)
    );
  });
  if (fof.checked) {
    neighbors = friendOfFriends(neighbors);
  }
  const newNodes = baseNodes.filter((node) => {
    return neighbors.indexOf(node.name_id) > -1;
  });

  const diff = {
    removed: nodes.filter((node) => newNodes.indexOf(node) === -1),
    added: newNodes.filter((node) => nodes.indexOf(node) === -1),
  };

  diff.removed.forEach((node) => nodes.splice(nodes.indexOf(node), 1));
  diff.added.forEach((node) => nodes.push(node));
}

function updateGraph() {
  // links
  linkElements = linkGroup.selectAll("line").data(links, (link) => {
    return link.target.name_id + link.source.name_id;
  });

  linkElements.exit().remove();

  const linkEnter = linkElements
    .enter()
    .append("line")
    .attr("stroke-width", 1)
    .attr("stroke", "rgba(50, 50, 50, 0.2)");

  linkElements = linkEnter.merge(linkElements);

  // nodes
  nodeElements = nodeGroup.selectAll("circle").data(nodes, (node) => {
    return node.name_id;
  });

  nodeElements.exit().remove();

  const nodeEnter = nodeElements
    .enter()
    .append("circle")
    .attr("r", (d) => {
      return getNodeSize(d);
    })
    .attr("fill", (x) => {
      return languageObject[x.language].normal;
    })
    .call(dragDrop)
    .on("click", selectNode);

  nodeElements = nodeEnter.merge(nodeElements);

  // texts
  textElements = textGroup.selectAll("text").data(nodes, (node) => {
    return node.name_id;
  });

  textElements.exit().remove();

  const textEnter = textElements
    .enter()
    .append("text")
    .text((node) => node.canonical_name)
    .attr("font-size", 15)
    .attr("dx", 15)
    .attr("dy", 4);

  textElements = textEnter.merge(textElements);
}

fof.addEventListener("click", function (e) {
  if (selectedId) {
    const selectedNode = baseNodes.find((x) => x.name_id === selectedId);
    updateData(selectedNode);
  }
  updateSimulation();
});

function updateSimulation() {
  updateGraph();

  simulation.nodes(nodes).on("tick", () => {
    nodeElements
      .attr("cx", (d) => {
        return (d.x = Math.max(r, Math.min(width - r, d.x)));
      })
      .attr("cy", (d) => {
        return (d.y = Math.max(r, Math.min(height - r, d.y)));
      });
    // .attr('cx', function (node) { return node.x })
    // .attr('cy', function (node) { return node.y })
    textElements
      .attr("x", function (node) {
        return node.x;
      })
      .attr("y", function (node) {
        return node.y;
      });
    linkElements
      .attr("x1", (link) => link.source.x)
      .attr("y1", (link) => link.source.y)
      .attr("x2", (link) => link.target.x)
      .attr("y2", (link) => link.target.y);
  });

  simulation.force("link").links(links);
  simulation.alphaTarget(0.2).restart();
}

function nameChooserFromLink(node) {
  selectedId = undefined;
  selectNode(node);
}
