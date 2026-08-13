// assets/ol-map.js

const loadScript = (src) =>
  new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = src;
    s.onload = res;
    s.onerror = rej;
    document.head.appendChild(s);
  });

const loadCss = (href) =>
  new Promise((res, rej) => {
    const l = document.createElement("link");
    l.rel = "stylesheet";
    l.href = href;
    l.onload = res;
    l.onerror = rej;
    document.head.appendChild(l);
  });

const waitForDiv = (id) =>
  new Promise((res) => {
    const tick = () => {
      const el = document.getElementById(id);
      if (el && el.offsetWidth > 0 && el.offsetHeight > 0) return res(el);
      requestAnimationFrame(tick);
    };
    tick();
  });

function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// ------------------------------------------------------------------
// LAYER REGISTRY
// ------------------------------------------------------------------
const LAYER_REGISTRY = [
  {
    id: "arrival_heights",
    group: "Arrival Heights",
    file: "ARRIVAL_HEIGHTS.geojson",
    status: "Active",
    color: "rgba(219, 135, 24, 0.9)",
    zIndex: 15,
    visible: true
  },
  {
    id: "CRARY_ICE_RISE",
    group: "Crary Ice Rise",
    file: "CRARY_ICE_RISE.geojson",
    status: "Active",
    color: "rgba(219, 135, 24, 0.9)",
    zIndex: 15,
    visible: true
  },
  {
    id: "KAMB_ICE_STREAM",
    group: "Kamb Ice Stream",
    file: "KAMB_ICE_STREAM.geojson",
    status: "Active",
    color: "rgba(219, 135, 24, 0.9)",
    zIndex: 15,
    visible: true
  },
  {
    id: "pyramid_trough",
    group: "Pyramid Trough",
    file: "PYRAMID_TROUGH.geojson",
    status: "Active",
    color: "rgba(219, 135, 24, 0.9)",
    zIndex: 15,
    visible: true
  },
  {
    id: "scott_base",
    group: "Scott Base",
    file: "SCOTT_BASE.geojson",
    status: "Active",
    color: "rgba(0, 180, 120, 0.9)",
    zIndex: 15,
    visible: true
  },
  {
    id: "K020A--BUDDAH_LAKE",
    group: "K020A - Virus Dispersal",
    file: "K020A--BUDDAH_LAKE.geojson",
    status: "Buddah Lake",
    color: "rgba(230, 180, 50, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K020A--MINNA_BLUFF",
    group: "K020A - Virus Dispersal",
    file: "K020A--MINNA_BLUFF.geojson",
    status: "Minna Bluff",
    color: "rgba(230, 180, 50, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K020A--PYRAMID_TROUGH",
    group: "K020A - Virus Dispersal",
    file: "K020A--PYRAMID_TROUGH.geojson",
    status: "Pyramid Trough",
    color: "rgba(230, 180, 50, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K022A--PLANNED",
    group: "K022A - Mount Erebus",
    file: "K022A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(255, 222, 33, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K026A--PYRAMID_TROUGH",
    group: "K026A - Ecosystem Mapping",
    file: "K026A--PYRAMID_TROUGH.geojson",
    status: "Pyramid Trough",
    color: "rgba(205, 100, 205, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K026A--LAKE_FRYXELL",
    group: "K026A - Ecosystem Mapping",
    file: "K026A--LAKE_FRYXELL.geojson",
    status: "Lake Fryxell",
    color: "rgba(205, 100, 205, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K044A--PLANNED",
    group: "K044A - Ice Cores",
    file: "K044A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(45, 220, 175, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K053A--PLANNED",
    group: "K053A - Pack-Ice Survey",
    file: "K053A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(210, 90, 255, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K055A--PLANNED",
    group: "K055A - Atmospheric Dynamics",
    file: "K055A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(100, 149, 237, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K060A--PLANNED",
    group: "K060A - VLF Sensors",
    file: "K060A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(255, 140, 0, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--BLOOD_FALLS",
    group: "K082A - Seafloor Seeps",
    file: "K082A--BLOOD_FALLS.geojson",
    status: "Blood Falls",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--CAPE_EVANS",
    group: "K082A - Seafloor Seeps",
    file: "K082A--CAPE_EVANS.geojson",
    status: "Cape Evans",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--GRANITE_HARBOUR",
    group: "K082A - Seafloor Seeps",
    file: "K082A--GRANITE_HARBOUR.geojson",
    status: "Granite Harbour",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--LAKE_FRYXELL",
    group: "K082A - Seafloor Seeps",
    file: "K082A--LAKE_FRYXELL.geojson",
    status: "Lake Fryxell",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--MCMURDO_SOUND",
    group: "K082A - Seafloor Seeps",
    file: "K082A--MCMURDO_SOUND.geojson",
    status: "McMurdo Sound",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K082A--NEW_HARBOUR",
    group: "K082A - Seafloor Seeps",
    file: "K082A--NEW_HARBOUR.geojson",
    status: "New Harbour",
    color: "rgba(40, 195, 200, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K085A--PLANNED",
    group: "K085A - Atmospheric Composition",
    file: "K085A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(147, 112, 219, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K089A--PLANNED",
    group: "K089A - AWS",
    file: "K089A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(130, 40, 240, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K102A--PLANNED",
    group: "K102A - Geomagnetic",
    file: "K102A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(255, 90, 40, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K150A--PLANNED",
    group: "K150A - GNSS & Tide Gauge",
    file: "K150A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(80, 160, 255, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K150B--PLANNED",
    group: "K150B - SouthPAN",
    file: "K150B--PLANNED.geojson",
    status: "Planned",
    color: "rgba(165, 160, 255, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K170A--PLANNED",
    group: "K170A - AHT",
    file: "K170A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(235, 110, 65, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K850A--PLANNED",
    group: "K850A - Penguin Census",
    file: "K850A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(230, 100, 145, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K865A--PLANNED",
    group: "K865A - GNSS",
    file: "K865A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(240, 40, 185, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K872B--PLANNED",
    group: "K872B – ApRES",
    file: "K872B--PLANNED.geojson",
    status: "Planned",
    color: "rgba(255, 120, 110, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K881B--PLANNED",
    group: "K881B - AWS",
    file: "K881B--PLANNED.geojson",
    status: "Planned",
    color: "rgba(20, 180, 240, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K882B--PLANNED",
    group: "K882B - Hauwai",
    file: "K882B--PLANNED.geojson",
    status: "Planned",
    color: "rgba(255, 180, 100, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K884A--PLANNED",
    group: "K884A - Sponges",
    file: "K884A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(60, 110, 235, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K891A--PLANNED",
    group: "K891A - Sea Ice",
    file: "K891A--PLANNED.geojson",
    status: "PLANNED",
    color: "rgba(20, 215, 195, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K893A--COMMONWEALTH_GLACIER",
    group: "K893A - Super Site",
    file: "K893A--COMMONWEALTH_GLACIER.geojson",
    status: "Commonwealth Glacier",
    color: "rgba(235, 30, 60, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K893A--LOWER_WRIGHT_GLACIER",
    group: "K893A - Super Site",
    file: "K893A--LOWER_WRIGHT_GLACIER.geojson",
    status: "Lower Wright Glacier",
    color: "rgba(235, 30, 60, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K893A--PYRAMID_TROUGH",
    group: "K893A - Super Site",
    file: "K893A--PYRAMID_TROUGH.geojson",
    status: "Pyramid Trough",
    color: "rgba(235, 30, 60, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "K894A--PLANNED",
    group: "K894A - Terrestrial Survey",
    file: "K894A--PLANNED.geojson",
    status: "Planned",
    color: "rgba(240, 170, 80, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "asp_planned",
    group: "Tangaroa - ASP Moorings",
    file: "ASP_MOORINGS-PLANNED_2027.geojson",
    status: "Planned",
    color: "rgba(30, 144, 255, 0.9)",
    filterStatus: "planned",
    zIndex: 20,
    visible: true,
  },
  {
    id: "CAMPSITES-2324",
    group: "Camp Sites",
    file: "CAMPSITES-2324.geojson",
    season: "2023-24",
    color: "rgba(255, 165, 0, 0.92)",
    isCampSite: true,
    zIndex: 5,
    visible: false,
  },
  {
    id: "CAMPSITES-2425",
    group: "Camp Sites",
    file: "CAMPSITES-2425.geojson",
    season: "2024-25",
    color: "rgba(255, 120, 0, 0.92)",
    isCampSite: true,
    zIndex: 5,
    visible: false,
  },
  {
    id: "CAMPSITES-2526",
    group: "Camp Sites",
    file: "CAMPSITES-2526.geojson",
    season: "2025-26",
    color: "rgba(220, 80, 0, 0.92)",
    isCampSite: true,
    zIndex: 5,
    visible: false,
  },
  {
    id: "instruments_active",
    group: "Instruments",
    file: "INSTALLATIONS_ACTIVE.geojson",
    status: "Active",
    color: "rgba(0, 200, 80, 0.95)",
    zIndex: 10,
    visible: false,
  },
  {
    id: "instruments_offline",
    group: "Instruments",
    file: "computed/offline.geojson",
    status: "Offline",
    color: "rgba(255, 165, 0, 0.9)",
    zIndex: 10,
    visible: false,
  },
  {
    id: "instruments_decommissioned",
    group: "Instruments",
    file: "INSTALLATIONS_DEACTIVATED.geojson",
    status: "Planned Removal",
    color: "rgba(255, 100, 0, 0.95)",
    zIndex: 10,
    visible: false,
  },
];

// ------------------------------------------------------------------
// POLYGON OVERLAY REGISTRY (ASPA / ASMA — Antarctic Treaty areas)
// ------------------------------------------------------------------
// ASMA drawn first (lower zIndex) so ASPAs — the smaller, more specific
// sites nested inside broader ASMA zones — sit on top.
const POLYGON_REGISTRY = [
  {
    id: "asma",
    shortLabel: "ASMA",
    label: "Antarctic Specially Managed Areas",
    file: "APA_ASMA.geojson",
    fill: "rgba(255, 220, 80, 0.14)",
    outline: "rgba(255, 225, 100, 0.9)",
    outlineWidth: 1.25,
    zIndex: 3,
  },
  {
    id: "aspa",
    shortLabel: "ASPA",
    label: "Antarctic Specially Protected Areas",
    file: "APA_ASPA.geojson",
    fill: "rgba(255, 100, 165, 0.15)",
    outline: "rgba(255, 130, 185, 0.9)",
    outlineWidth: 1.25,
    zIndex: 4,
  },
];

// ------------------------------------------------------------------
// Scale-dependent point style (cached per radius bucket)
// ------------------------------------------------------------------
function makeScaledPointStyle(fillColor) {
  const cache = {};
  return function (feature, resolution) {
    const radius = Math.max(3, Math.min(10, 8000 / resolution));
    const key = Math.round(radius);
    if (!cache[key]) {
      cache[key] = new ol.style.Style({
        image: new ol.style.Circle({
          radius,
          fill: new ol.style.Fill({ color: fillColor }),
          stroke: new ol.style.Stroke({
            color: "white",
            width: Math.max(1, radius / 3),
          }),
        }),
      });
    }
    return cache[key];
  };
}

// ------------------------------------------------------------------
// Active instruments event filter — module-scope so buildLayer and
// setLayerVisibility can both reference it.
// ------------------------------------------------------------------
let __instruments_active_events__ = [];

// Manifest of --ACTIVE.geojson files that actually exist on disk.
// Populated once at startup so buildLayer skips fetches for missing pairs.
const ACTIVE_MANIFEST = new Set();

const instrumentsActiveStyleFn = (function () {
  const cache = {};
  return function (feature, resolution) {
    if (__instruments_active_events__.length > 0) {
      const evt = feature.get("event") || "";
      if (!__instruments_active_events__.includes(evt)) return null;
    }
    const radius = Math.max(3, Math.min(10, 8000 / resolution));
    const key = Math.round(radius);
    if (!cache[key]) {
      cache[key] = new ol.style.Style({
        image: new ol.style.Circle({
          radius,
          fill: new ol.style.Fill({ color: "rgba(0, 200, 80, 0.95)" }),
          stroke: new ol.style.Stroke({ color: "white", width: Math.max(1, radius / 3) }),
        }),
      });
    }
    return cache[key];
  };
})();

// ------------------------------------------------------------------
// Location layer dedup: hide features already shown by active science
// event layers so the same point never renders twice.
// ------------------------------------------------------------------
const SCIENCE_EVENT_CODES = {}; // layerId → K-event code
for (const entry of LAYER_REGISTRY) {
  if (entry.filterStatus === "planned") {
    const parts = (entry.group || "").split(" - ");
    if (parts.length >= 2) SCIENCE_EVENT_CODES[entry.id] = parts[0].trim();
  }
}

const LOCATION_LAYER_IDS = new Set([
  "arrival_heights", "pyramid_trough", "scott_base",
  "KAMB_ICE_STREAM", "CRARY_ICE_RISE",
]);

let __covered_event_codes__ = new Set();

function refreshCoveredEventCodes() {
  __covered_event_codes__ = new Set();
  if (!window.__ol_map__) return;
  window.__ol_map__.getLayers().getArray().forEach(function (layer) {
    const id = layer.get("id");
    if (SCIENCE_EVENT_CODES[id] !== undefined && layer.getVisible()) {
      __covered_event_codes__.add(SCIENCE_EVENT_CODES[id]);
    }
  });
}

function makeLocationLayerStyle(fillColor) {
  const cache = {};
  return function (feature, resolution) {
    const eventCode = feature.get("event") || "";
    if (eventCode && __covered_event_codes__.has(eventCode)) return null;
    const radius = Math.max(3, Math.min(10, 8000 / resolution));
    const key = Math.round(radius);
    if (!cache[key]) {
      cache[key] = new ol.style.Style({
        image: new ol.style.Circle({
          radius,
          fill: new ol.style.Fill({ color: fillColor }),
          stroke: new ol.style.Stroke({ color: "white", width: Math.max(1, radius / 3) }),
        }),
      });
    }
    return cache[key];
  };
}

// ------------------------------------------------------------------
// Build one OL vector layer from a registry entry
// ------------------------------------------------------------------
function buildLayer(entry) {
  const source = new ol.source.Vector();
  const projOpts = { dataProjection: "EPSG:4326", featureProjection: "EPSG:3031" };

  fetch(`/assets/${entry.file}`)
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status} loading ${entry.file}`);
      return r.json();
    })
    .then((json) => {
      let features = new ol.format.GeoJSON().readFeatures(json, projOpts);
      if (entry.filterStatus) {
        const fs = entry.filterStatus.toLowerCase();
        features = features.filter(f =>
          String(f.get("status") || "").toLowerCase() === fs
        );
      }
      if (entry.isCampSite) {
        features.forEach(f => f.set("__isCampSite__", true));
      }
      console.log(`Loaded "${entry.id}" (${entry.status || entry.season}): ${features.length} features`);
      source.addFeatures(features);
    })
    .catch((err) => console.error(`Layer "${entry.id}" load error:`, err));

  if (entry.filterStatus === "planned" && entry.file.endsWith("--PLANNED.geojson")) {
    const activeFile = entry.file.replace("--PLANNED.geojson", "--ACTIVE.geojson");
    if (ACTIVE_MANIFEST.has(activeFile)) {
      fetch(`/assets/${activeFile}`)
        .then((r) => r.ok ? r.json() : null)
        .then((json) => {
          if (!json) return;
          const features = new ol.format.GeoJSON().readFeatures(json, projOpts);
          source.addFeatures(features);
        })
        .catch((err) => console.error(`Layer "${entry.id}" ACTIVE load error:`, err));
    }
  }

  const style = entry.id === "instruments_active"
    ? instrumentsActiveStyleFn
    : LOCATION_LAYER_IDS.has(entry.id)
      ? makeLocationLayerStyle(entry.color)
      : makeScaledPointStyle(entry.color);

  const layer = new ol.layer.Vector({
    source,
    style,
    visible: false,
    zIndex: entry.zIndex !== undefined ? entry.zIndex : 1,
  });
  layer.set("id", entry.id);
  layer.set("status", entry.status);
  return layer;
}

// ------------------------------------------------------------------
// Build one OL polygon overlay layer (ASPA / ASMA)
// ------------------------------------------------------------------
function buildPolygonLayer(entry) {
  const source = new ol.source.Vector();
  const projOpts = { dataProjection: "EPSG:4326", featureProjection: "EPSG:3031" };

  fetch(`/assets/${entry.file}`)
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status} loading ${entry.file}`);
      return r.json();
    })
    .then((json) => {
      const features = new ol.format.GeoJSON().readFeatures(json, projOpts);
      features.forEach((f) => f.set("__polygonLayerId__", entry.id));
      source.addFeatures(features);
      console.log(`Loaded polygon overlay "${entry.id}": ${features.length} features`);
    })
    .catch((err) => console.error(`Polygon overlay "${entry.id}" load error:`, err));

  const style = new ol.style.Style({
    fill: new ol.style.Fill({ color: entry.fill }),
    stroke: new ol.style.Stroke({ color: entry.outline, width: entry.outlineWidth }),
  });

  const layer = new ol.layer.Vector({
    source,
    style,
    visible: false,
    zIndex: entry.zIndex,
  });
  layer.set("id", entry.id);
  layer.set("__isPolygonOverlay__", true);
  return layer;
}

// ------------------------------------------------------------------
// Main
// ------------------------------------------------------------------
(async () => {
  await loadCss("https://cdn.jsdelivr.net/npm/ol@latest/ol.css");
  await loadScript("https://cdn.jsdelivr.net/npm/proj4@2.11.0/dist/proj4.js");
  await loadScript("https://cdn.jsdelivr.net/npm/ol@latest/dist/ol.js");

  const target = await waitForDiv("ol-map");

  // ---- Popup -------------------------------------------------------
  const popupContainer = document.createElement("div");
  popupContainer.className = "ol-popup";
  popupContainer.style.display = "none";

  const popupCloseBtn = document.createElement("button");
  popupCloseBtn.className = "ol-popup__close";
  popupCloseBtn.innerHTML = "&#10005;";
  popupCloseBtn.title = "Close";
  popupCloseBtn.setAttribute("aria-label", "Close popup");
  popupCloseBtn.addEventListener("click", function () {
    popupContainer.style.display = "none";
    popupOverlay.setPosition(undefined);
  });

  const popupContent = document.createElement("div");
  popupContent.className = "ol-popup__content";
  popupContent.id = "ol-popup-content";

  popupContainer.appendChild(popupCloseBtn);
  popupContainer.appendChild(popupContent);
  target.appendChild(popupContainer);

  const popupOverlay = new ol.Overlay({
    element: popupContainer,
    positioning: "bottom-center",
    stopEvent: false,
    offset: [0, -12],
  });

  // ---- Projection --------------------------------------------------
  proj4.defs(
    "EPSG:3031",
    "+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +datum=WGS84 +units=m +no_defs"
  );
  ol.proj.proj4.register(proj4);

  const projection3031 = ol.proj.get("EPSG:3031");
  const antarcticaExtent = [-4194304, -4194304, 4194304, 4194304];
  projection3031.setExtent(antarcticaExtent);

  // ---- Basemap registry --------------------------------------------
  // `attribution` is threaded onto the WMTS source so OL's built-in
  // .ol-attribution widget shows only the visible basemap's credit.
  const BASEMAP_REGISTRY = [
    {
      id: "esri_imagery",
      label: "ESRI Satellite",
      capsUrl: "https://services.arcgisonline.com/arcgis/rest/services/Polar/Antarctic_Imagery/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
      format: "image/jpg",
      attribution: "Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community.",
    },
    {
      id: "bas",
      label: "BAS Satellite",
      capsUrl: "https://tiles.arcgis.com/tiles/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/Antarctica_and_the_Southern_Ocean/MapServer/wmts?SERVICE=WMTS&REQUEST=GetCapabilities",
      format: "image/png",
      attribution: "Produced by the Mapping and Geographic Information Centre, British Antarctic Survey, 2025, version 1.",
    },
    {
      id: "landcare_ramp_rema",
      label: "Landcare RAMP/REMA",
      capsUrl: "https://prod-ada-3.landcareresearch.co.nz/mapcache/atda/wmts/1.0.0/WMTSCapabilities.xml",
      layerName: "ada_basemap_combined-HDPI",
      format: "image/png; mode=8bit",
      attribution: "© Landcare Research NZ Ltd CC BY 3.0 NZ. Basemap data from RAMP, via NSIDC, & REMA from Byrd Polar and Climate Research Center and the Polar Geospatial Center.",
    },
  ];

  async function loadBasemapLayer(entry) {
    try {
      const resp = await fetch(entry.capsUrl);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const xml = await resp.text();
      const caps = new ol.format.WMTSCapabilities().read(xml);
      const layerName = entry.layerName || caps.Contents.Layer[0].Identifier;
      const options = ol.source.WMTS.optionsFromCapabilities(caps, {
        layer: layerName,
        format: entry.format,
        crossOrigin: "anonymous",
      });
      if (entry.attribution) options.attributions = entry.attribution;
      const layer = new ol.layer.Tile({ source: new ol.source.WMTS(options) });
      layer.set("basemap-id", entry.id);
      return layer;
    } catch (err) {
      console.error(`Basemap "${entry.id}" load error:`, err);
      const layer = new ol.layer.Tile({
        source: new ol.source.TileDebug({ projection: projection3031 }),
      });
      layer.set("basemap-id", entry.id);
      return layer;
    }
  }

  const baseLayers = await Promise.all(BASEMAP_REGISTRY.map(loadBasemapLayer));
  baseLayers.forEach((l) => l.setVisible(l.get("basemap-id") === "esri_imagery"));

  // ---- Load ACTIVE manifest before building layers -----------------
  try {
    const resp = await fetch("/assets/computed/active_manifest.json");
    if (resp.ok) {
      const files = await resp.json();
      files.forEach((f) => ACTIVE_MANIFEST.add(f));
    }
  } catch (err) {
    console.error("ACTIVE manifest load error:", err);
  }

  // ---- Build all data layers from registry -------------------------
  const dataLayers = LAYER_REGISTRY.map(buildLayer);
  const polygonLayers = POLYGON_REGISTRY.map(buildPolygonLayer);

  // ---- Map ---------------------------------------------------------
  const map = new ol.Map({
    target,
    layers: [...baseLayers, ...polygonLayers, ...dataLayers],
    view: new ol.View({
      projection: projection3031,
      center: [0, 0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 11,
      extent: antarcticaExtent,
    }),
  });

  map.addOverlay(popupOverlay);
  window.__ol_map__ = map;

  // Replace OL's default (non-collapsible on wide screens) Attribution
  // control with one that starts collapsed — user clicks the "i" toggle
  // to expand and read the active basemap's credit.
  map.getControls().getArray().slice().forEach(function (c) {
    if (c instanceof ol.control.Attribution) map.removeControl(c);
  });
  map.addControl(new ol.control.Attribution({ collapsible: true, collapsed: true }));

  // ---- Basemap switcher -------------------------------------------
  let activeBasemapId = "esri_imagery";

  window.switchBasemap = function (selectedId) {
    if (selectedId === activeBasemapId) return;
    baseLayers.forEach((l) => l.setVisible(l.get("basemap-id") === selectedId));
    activeBasemapId = selectedId;
    renderBmPanel();
  };

  function renderBmPanel() {
    const panel = document.getElementById("bm-panel");
    if (!panel) return;
    panel.innerHTML = `
      <div class="bm-panel__heading">Base map</div>
      ${BASEMAP_REGISTRY.map(entry => `
        <button class="bm-option${entry.id === activeBasemapId ? " bm-option--active" : ""}"
                onclick="window.switchBasemap('${entry.id}')">
          ${entry.id === activeBasemapId ? "&#10003; " : ""}${entry.label}
        </button>`).join("")}`;
  }

  // ---- Basemap control button (right side, below zoom) ------------
  const globeIconSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" stroke-width="1.8"
         stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="9"/>
      <ellipse cx="12" cy="12" rx="4" ry="9"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
    </svg>`;

  const layersIconSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" stroke-width="1.8"
         stroke-linecap="round" stroke-linejoin="round">
      <polygon points="12 2 2 7 12 12 22 7 12 2"/>
      <polyline points="2 12 12 17 22 12"/>
      <polyline points="2 17 12 22 22 17"/>
    </svg>`;

  const waitForZoom = () => new Promise((res) => {
    const tick = () => {
      const el = target.querySelector(".ol-zoom");
      if (el) return res(el);
      setTimeout(tick, 80);
    };
    tick();
  });

  const zoomEl = await waitForZoom();

  const basemapsControl = document.createElement("div");
  // NOTE: Do NOT add ol-unselectable — OL sets pointer-events:none on it,
  // which swallows all clicks and makes the button invisible to the mouse.
  basemapsControl.id = "basemaps-control";
  basemapsControl.className = "ol-basemaps-control";
  basemapsControl.style.pointerEvents = "auto";
  basemapsControl.innerHTML = `
    <button class="ol-layers-btn" title="Basemaps" aria-label="Switch basemap" style="pointer-events:auto;">
      ${globeIconSvg}
    </button>
    <div class="bm-panel" id="bm-panel" style="display:none;"></div>`;

  zoomEl.parentNode.insertBefore(basemapsControl, zoomEl.nextSibling);
  renderBmPanel();

  // Block ALL mouse events from falling through to the map (prevents double-click zoom etc.)
  ["click", "dblclick", "mousedown", "mouseup", "pointerdown", "pointerup"].forEach(function (evtName) {
    basemapsControl.addEventListener(evtName, function (e) {
      e.stopPropagation();
    });
  });

  // Toggle the panel on button click; close the overlays menu if it's open
  // so the two panels never overlap.
  basemapsControl.querySelector(".ol-layers-btn").addEventListener("click", function (e) {
    e.stopPropagation();
    const panel = document.getElementById("bm-panel");
    const otherMenu = document.getElementById("overlays-menu");
    const isOpen = panel.style.display !== "none";
    if (otherMenu) otherMenu.style.display = "none";
    panel.style.display = isOpen ? "none" : "block";
  });

  // Close panel when clicking anywhere else on the map
  target.addEventListener("click", function () {
    const panel = document.getElementById("bm-panel");
    if (panel) panel.style.display = "none";
    const overlayMenu = document.getElementById("overlays-menu");
    if (overlayMenu) overlayMenu.style.display = "none";
  });

  // ---- Overlays control (ASPA / ASMA polygon toggles) --------------
  const overlaysControl = document.createElement("div");
  overlaysControl.id = "overlays-control";
  overlaysControl.className = "ol-overlays-control";
  overlaysControl.style.pointerEvents = "auto";
  overlaysControl.innerHTML = `
    <button class="ol-layers-btn" title="Overlay layers" aria-label="Toggle map overlay layers" style="pointer-events:auto;">
      ${layersIconSvg}
    </button>
    <div class="overlays-menu" id="overlays-menu" style="display:none;">
      <div class="overlays-menu__heading">Layers</div>
      ${POLYGON_REGISTRY.map(entry => `
        <label class="overlays-menu__item">
          <input type="checkbox" class="overlays-menu__checkbox"
                 data-polygon-id="${entry.id}">
          <span class="overlays-menu__swatch"
                style="background:${entry.fill};border-color:${entry.outline};"></span>
          <span class="overlays-menu__label">
            <span class="overlays-menu__short">${entry.shortLabel}</span>
            <span class="overlays-menu__full">${entry.label}</span>
          </span>
        </label>`).join("")}
    </div>`;

  basemapsControl.parentNode.insertBefore(overlaysControl, basemapsControl.nextSibling);

  ["click", "dblclick", "mousedown", "mouseup", "pointerdown", "pointerup"].forEach(function (evtName) {
    overlaysControl.addEventListener(evtName, function (e) {
      e.stopPropagation();
    });
  });

  overlaysControl.querySelector(".ol-layers-btn").addEventListener("click", function (e) {
    e.stopPropagation();
    const menu = document.getElementById("overlays-menu");
    const otherPanel = document.getElementById("bm-panel");
    const isOpen = menu.style.display !== "none";
    if (otherPanel) otherPanel.style.display = "none";
    menu.style.display = isOpen ? "none" : "block";
  });

  overlaysControl.querySelectorAll(".overlays-menu__checkbox").forEach((cb) => {
    cb.addEventListener("change", function () {
      const id = cb.dataset.polygonId;
      const layer = polygonLayers.find((l) => l.get("id") === id);
      if (layer) layer.setVisible(cb.checked);
    });
  });

  // ---- Ruler / measure tool ----------------------------------------
  const rulerIconSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
         fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
      <rect x="2" y="8" width="20" height="8" rx="1.5"/>
      <line x1="6" y1="8" x2="6" y2="11"/>
      <line x1="10" y1="8" x2="10" y2="12.5"/>
      <line x1="14" y1="8" x2="14" y2="11"/>
      <line x1="18" y1="8" x2="18" y2="12.5"/>
    </svg>`;

  const measureSource = new ol.source.Vector();
  const measureLayer = new ol.layer.Vector({
    source: measureSource,
    style: new ol.style.Style({
      stroke: new ol.style.Stroke({ color: "rgba(255,255,255,0.9)", width: 2, lineDash: [8, 6] }),
      image: new ol.style.Circle({
        radius: 4,
        fill: new ol.style.Fill({ color: "#fff" }),
        stroke: new ol.style.Stroke({ color: "rgba(0,0,0,0.25)", width: 1 }),
      }),
    }),
    zIndex: 200,
  });
  map.addLayer(measureLayer);

  const measureTooltipEl = document.createElement("div");
  measureTooltipEl.className = "measure-tooltip";
  const measureTooltipOverlay = new ol.Overlay({
    element: measureTooltipEl,
    offset: [12, -8],
    positioning: "center-left",
    stopEvent: false,
  });
  map.addOverlay(measureTooltipOverlay);

  const rulerControl = document.createElement("div");
  rulerControl.id = "ruler-control";
  rulerControl.className = "ol-ruler-control";
  rulerControl.style.pointerEvents = "auto";
  rulerControl.innerHTML = `
    <button class="ol-layers-btn ol-ruler-btn" title="Measure distance" aria-label="Measure distance" style="pointer-events:auto;">
      ${rulerIconSvg}
    </button>`;
  overlaysControl.parentNode.insertBefore(rulerControl, overlaysControl.nextSibling);

  ["click", "dblclick", "mousedown", "mouseup", "pointerdown", "pointerup"].forEach(function (evtName) {
    rulerControl.addEventListener(evtName, function (e) { e.stopPropagation(); });
  });

  const rulerBtn = rulerControl.querySelector(".ol-ruler-btn");
  let drawInteraction = null;
  let measureSketch = null;
  let rulerActive = false;

  function formatDist(m) {
    return m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`;
  }

  function onMeasurePointerMove(e) {
    if (!measureSketch) return;
    const dist = ol.sphere.getLength(measureSketch.getGeometry(), { projection: "EPSG:3031" });
    measureTooltipEl.textContent = formatDist(dist);
    measureTooltipOverlay.setPosition(e.coordinate);
  }

  function clearMeasure() {
    measureSource.clear();
    measureTooltipEl.className = "measure-tooltip";
    measureTooltipEl.textContent = "";
    measureTooltipOverlay.setPosition(undefined);
  }

  function activateMeasure() {
    rulerActive = true;
    rulerBtn.classList.add("ol-ruler-btn--active");
    map.getViewport().style.cursor = "crosshair";
    clearMeasure();
    popupContainer.style.display = "none";
    popupOverlay.setPosition(undefined);

    drawInteraction = new ol.interaction.Draw({
      source: measureSource,
      type: "LineString",
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({ color: "rgba(255,255,255,0.85)", width: 2, lineDash: [6, 5] }),
        image: new ol.style.Circle({
          radius: 4,
          fill: new ol.style.Fill({ color: "#fff" }),
          stroke: new ol.style.Stroke({ color: "rgba(0,0,0,0.3)", width: 1 }),
        }),
      }),
    });
    map.addInteraction(drawInteraction);
    map.on("pointermove", onMeasurePointerMove);

    drawInteraction.on("drawstart", function (e) {
      measureSketch = e.feature;
    });

    drawInteraction.on("drawend", function (e) {
      const geom = e.feature.getGeometry();
      const coords = geom.getCoordinates();
      const dist = ol.sphere.getLength(geom, { projection: "EPSG:3031" });
      measureTooltipEl.textContent = formatDist(dist);
      measureTooltipEl.className = "measure-tooltip measure-tooltip--final";
      measureTooltipOverlay.setPosition(coords[coords.length - 1]);
      measureSketch = null;
      map.un("pointermove", onMeasurePointerMove);
      map.removeInteraction(drawInteraction);
      drawInteraction = null;
      map.getViewport().style.cursor = "";
      rulerActive = false;
      rulerBtn.classList.remove("ol-ruler-btn--active");
    });
  }

  function deactivateMeasure() {
    if (drawInteraction) {
      drawInteraction.abortDrawing();
      map.removeInteraction(drawInteraction);
      drawInteraction = null;
    }
    map.un("pointermove", onMeasurePointerMove);
    map.getViewport().style.cursor = "";
    rulerActive = false;
    rulerBtn.classList.remove("ol-ruler-btn--active");
    measureSketch = null;
    clearMeasure();
  }

  rulerBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    if (rulerActive || measureSource.getFeatures().length > 0) {
      deactivateMeasure();
    } else {
      activateMeasure();
    }
  });

  // ---- Popup helpers -----------------------------------------------
  function renderFeaturePage(props, pageIndex, total) {
    const site = props.name || "Location";
    const measurement = props.description || null;
    const event = props.event || null;
    const statuses = props.__statuses__ || [props.status || "—"];
    const pi = props["principal investigator"] || "—";
    const email = props.email || "—";

    function statusBadge(s) {
      const sl = String(s).toLowerCase();
      const cls = sl === "active" ? "status-badge status-badge--active" :
        sl === "wishlist" ? "status-badge status-badge--wishlist" :
        sl === "planned" ? "status-badge status-badge--planned" :
        sl === "planned removal" ? "status-badge status-badge--planned-removal" :
        "status-badge";
      return `<span class="${cls}">${escapeHtml(s)}</span>`;
    }
    const statusBadgesHtml = statuses.map(statusBadge).join(" ");

    const site_name = props.site || null;
    const information = props.information || null;
    const siteEsc = escapeHtml(site);
    const piEsc = escapeHtml(pi);
    const emailEsc = escapeHtml(email);
    const measurementEsc = measurement ? escapeHtml(measurement) : null;
    const eventEsc = event ? escapeHtml(event) : null;
    const siteNameEsc = site_name ? escapeHtml(site_name) : null;
    // Only allow http/https URLs to prevent javascript: injection
    const informationUrl = information && /^https?:\/\//i.test(information)
      ? escapeHtml(information) : null;

    const coords = props.__coords__;
    const coordsAttr = coords
      ? `${coords[1].toFixed(6)}, ${coords[0].toFixed(6)}`
      : null;
    const coordsRowHtml = coordsAttr ? `
      <div class="popup-info-row">
        <button class="copy-coords-btn" data-coords="${coordsAttr}" title="Copy coordinates (lat, lon) to clipboard" aria-label="Copy coordinates">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <span class="copy-coords-label">Get Coordinates</span>
        </button>
      </div>` : "";
    const infoRowHtml = informationUrl ? `
      <div class="popup-info-row">
        <a class="popup-info-link" href="${informationUrl}" target="_blank" rel="noopener noreferrer">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
          More Information
        </a>
      </div>` : "";
    const infoSectionHtml = (coordsRowHtml || infoRowHtml)
      ? `<div class="popup-info">${coordsRowHtml}${infoRowHtml}</div>`
      : "";

    const paginationHtml = total > 1 ? `
      <div class="popup-pagination">
        <button class="popup-nav-btn" id="popup-prev" ${pageIndex === 0 ? "disabled" : ""}>&#8592;</button>
        <span class="popup-page-indicator">${pageIndex + 1} / ${total}</span>
        <button class="popup-nav-btn" id="popup-next" ${pageIndex === total - 1 ? "disabled" : ""}>&#8594;</button>
      </div>` : "";

    popupContent.innerHTML = `
      ${paginationHtml}
      <div class="popup-title">${siteEsc}</div>
      ${siteNameEsc ? `<div class="popup-site"><strong>Site:</strong> ${siteNameEsc}</div>` : ""}
      ${eventEsc ? `<div class="popup-event"><strong>Event:</strong> ${eventEsc}</div>` : ""}
      <div class="popup-status">
        <strong>Status:</strong>
        ${statusBadgesHtml}
      </div>
      ${measurementEsc ? `<div class="popup-measurement"><strong>Description:</strong> ${measurementEsc}</div>` : ""}
      <div class="popup-pi"><strong>Contact:</strong> ${piEsc}</div>
      <div class="popup-email">
        <strong>Email:</strong>
        <span class="email-text">${emailEsc}</span>
        <button class="copy-email-btn" data-email="${emailEsc}" title="Copy email to clipboard" aria-label="Copy email">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
      ${infoSectionHtml}
    `;

    if (total > 1) {
      document.getElementById("popup-prev").addEventListener("click", function () {
        window.__popup_page__ = Math.max(0, window.__popup_page__ - 1);
        renderFeaturePage(
          window.__popup_features__[window.__popup_page__],
          window.__popup_page__,
          window.__popup_features__.length
        );
      });
      document.getElementById("popup-next").addEventListener("click", function () {
        window.__popup_page__ = Math.min(total - 1, window.__popup_page__ + 1);
        renderFeaturePage(
          window.__popup_features__[window.__popup_page__],
          window.__popup_page__,
          window.__popup_features__.length
        );
      });
    }
  }

  function renderCampSitePage(props, pageIndex, total) {
    const site    = props.site    ? escapeHtml(props.site)    : null;
    const event   = props.event   ? escapeHtml(props.event)   : "—";
    const season  = props.season  ? escapeHtml(props.season)  : "—";

    const paginationHtml = total > 1 ? `
      <div class="popup-pagination">
        <button class="popup-nav-btn" id="popup-prev" ${pageIndex === 0 ? "disabled" : ""}>&#8592;</button>
        <span class="popup-page-indicator">${pageIndex + 1} / ${total}</span>
        <button class="popup-nav-btn" id="popup-next" ${pageIndex === total - 1 ? "disabled" : ""}>&#8594;</button>
      </div>` : "";

    popupContent.innerHTML = `
      ${paginationHtml}
      <div class="popup-title">Camp Site${site ? ": " + site : ""}</div>
      <div><strong>Event:</strong> ${event}</div>
      <div><strong>Season:</strong> ${season}</div>
    `;

    if (total > 1) {
      document.getElementById("popup-prev").addEventListener("click", function () {
        window.__popup_page__ = Math.max(0, window.__popup_page__ - 1);
        const p = window.__popup_features__[window.__popup_page__];
        (p.__isCampSite__ ? renderCampSitePage : renderFeaturePage)(p, window.__popup_page__, total);
      });
      document.getElementById("popup-next").addEventListener("click", function () {
        window.__popup_page__ = Math.min(total - 1, window.__popup_page__ + 1);
        const p = window.__popup_features__[window.__popup_page__];
        (p.__isCampSite__ ? renderCampSitePage : renderFeaturePage)(p, window.__popup_page__, total);
      });
    }
  }

  // ---- Polygon hover tooltip (ASPA / ASMA) -------------------------
  const polygonTooltipEl = document.createElement("div");
  polygonTooltipEl.className = "polygon-tooltip";
  polygonTooltipEl.style.display = "none";
  const polygonTooltipOverlay = new ol.Overlay({
    element: polygonTooltipEl,
    offset: [12, 0],
    positioning: "center-left",
    stopEvent: false,
  });
  map.addOverlay(polygonTooltipOverlay);

  const POLYGON_META = Object.fromEntries(
    POLYGON_REGISTRY.map((e) => [e.id, e])
  );

  map.on("pointermove", function (evt) {
    if (evt.dragging || rulerActive) {
      polygonTooltipEl.style.display = "none";
      return;
    }
    let hit = null;
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      const layerId = feature.get("__polygonLayerId__");
      if (!layerId) return;
      hit = { feature, layerId };
      return true;
    }, { hitTolerance: 0 });

    if (!hit) {
      polygonTooltipEl.style.display = "none";
      return;
    }

    const meta = POLYGON_META[hit.layerId];
    const props = hit.feature.getProperties();
    const name = props.Name || "Unnamed";
    const area = props.Area_km;
    const areaStr = (typeof area === "number") ? `${area.toLocaleString(undefined, {maximumFractionDigits: 2})} km²` : "—";
    const marine = String(props.Marine) === "1" ? "Marine" : "Terrestrial";
    polygonTooltipEl.innerHTML = `
      <div class="polygon-tooltip__type">${escapeHtml(meta.label)}</div>
      <div class="polygon-tooltip__name">${escapeHtml(name)}</div>
      <div class="polygon-tooltip__meta">${marine} &middot; ${areaStr}</div>`;
    polygonTooltipEl.style.display = "block";
    polygonTooltipOverlay.setPosition(evt.coordinate);
  });

  // ---- Popup click handler -----------------------------------------
  map.on("singleclick", function (evt) {
    if (rulerActive) return;
    popupOverlay.setPosition(undefined);
    popupContainer.style.display = "none";

    const rawFeatures = [];
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      // Polygon overlays (ASPA/ASMA) use a separate hover tooltip.
      if (feature.get("__polygonLayerId__")) return;
      const props = feature.getProperties();
      const geom = feature.getGeometry();
      if (geom && geom.getType() === "Point") {
        const [lon, lat] = ol.proj.toLonLat(geom.getCoordinates(), "EPSG:3031");
        props.__coords__ = [lon, lat];
      }
      rawFeatures.push(props);
    }, { hitTolerance: 10 });

    if (rawFeatures.length === 0) return;

    const seen = new Map();
    const featuresAtPixel = [];
    for (const props of rawFeatures) {
      const key = (props.event || "") + "::" + (props.name || "") + "::" + (props.site || "");
      if (seen.has(key)) {
        const existing = seen.get(key);
        const cur = existing.__statuses__ || [existing.status];
        if (!cur.includes(props.status)) existing.__statuses__ = [...cur, props.status];
        if (!existing.__coords__ && props.__coords__) existing.__coords__ = props.__coords__;
      } else {
        const merged = { ...props };
        seen.set(key, merged);
        featuresAtPixel.push(merged);
      }
    }

    window.__popup_features__ = featuresAtPixel;
    window.__popup_page__ = 0;

    const firstProps = featuresAtPixel[0];
    if (firstProps.__isCampSite__) {
      renderCampSitePage(firstProps, 0, featuresAtPixel.length);
    } else {
      renderFeaturePage(firstProps, 0, featuresAtPixel.length);
    }
    popupOverlay.setPosition(evt.coordinate);
    popupContainer.style.display = "block";
  });
})();

// ---- Copy-to-clipboard -------------------------------------------
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".copy-email-btn, .copy-coords-btn");
  if (!btn) return;
  const value = btn.dataset.email || btn.dataset.coords;
  if (!value) return;
  navigator.clipboard.writeText(value).then(() => {
    const oldHtml = btn.innerHTML;
    btn.classList.add("copied");
    btn.textContent = "Copied";
    setTimeout(() => {
      btn.innerHTML = oldHtml;
      btn.classList.remove("copied");
    }, 1200);
  });
});

// ---- Layer visibility (called from Dash store callback) ----------
window.setLayerVisibility = function (layerId, visible) {
  if (!window.__ol_map__) return;
  if (layerId === "__active_events__") {
    __instruments_active_events__ = Array.isArray(visible) ? visible : [];
    window.__ol_map__.getLayers().getArray().forEach(function (layer) {
      if (layer.get("id") === "instruments_active") layer.changed();
    });
    window.__ol_map__.render();
    return;
  }
  window.__ol_map__.getLayers().getArray().forEach(function (layer) {
    if (layer.get("id") === layerId) layer.setVisible(!!visible);
  });
  // When a science event layer changes visibility, refresh which event codes
  // are covered so location layers can filter out duplicate features.
  if (SCIENCE_EVENT_CODES[layerId] !== undefined) {
    refreshCoveredEventCodes();
    window.__ol_map__.getLayers().getArray().forEach(function (layer) {
      if (LOCATION_LAYER_IDS.has(layer.get("id"))) layer.changed();
    });
    window.__ol_map__.render();
  }
};