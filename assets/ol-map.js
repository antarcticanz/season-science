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

(async () => {
  await loadCss("https://cdn.jsdelivr.net/npm/ol@latest/ol.css");
  await loadScript("https://cdn.jsdelivr.net/npm/proj4@2.11.0/dist/proj4.js");
  await loadScript("https://cdn.jsdelivr.net/npm/ol@latest/dist/ol.js");

  const target = await waitForDiv("ol-map");

  // ------------------------------------------------------------------
  // Popup container + overlay (✅ added / fixed)
  // ------------------------------------------------------------------
  const popupContainer = document.createElement("div");
  popupContainer.className = "ol-popup";
  popupContainer.style.display = "none";

  const popupContent = document.createElement("div");
  popupContent.className = "ol-popup__content";

  popupContainer.appendChild(popupContent);
  target.appendChild(popupContainer);

  const popupOverlay = new ol.Overlay({
    element: popupContainer,
    positioning: "bottom-center",
    stopEvent: false,
    offset: [0, -12],
  });

  // ------------------------------------------------------------------
  // EPSG:3031
  // ------------------------------------------------------------------
  proj4.defs(
    "EPSG:3031",
    "+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +datum=WGS84 +units=m +no_defs"
  );
  ol.proj.proj4.register(proj4);

  const projection3031 = ol.proj.get("EPSG:3031");
  const antarcticaExtent = [-4194304, -4194304, 4194304, 4194304];
  projection3031.setExtent(antarcticaExtent);

  // ------------------------------------------------------------------
  // BAS WMTS
  // ------------------------------------------------------------------
  const BAS_WMTS_URL =
    "https://tiles.arcgis.com/tiles/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/Antarctica_and_the_Southern_Ocean/MapServer/wmts?SERVICE=WMTS&REQUEST=GetCapabilities";

  let basLayer;
  try {
    const resp = await fetch(BAS_WMTS_URL);
    const xml = await resp.text();
    const caps = new ol.format.WMTSCapabilities().read(xml);

    const layerName = caps.Contents.Layer[0].Identifier;

    const options = ol.source.WMTS.optionsFromCapabilities(caps, {
      layer: layerName,
      format: "image/png",
      crossOrigin: "anonymous",
    });

    basLayer = new ol.layer.Tile({
      source: new ol.source.WMTS(options),
    });
  } catch (err) {
    console.error("WMTS error:", err);
    basLayer = new ol.layer.Tile({
      source: new ol.source.TileDebug({ projection: projection3031 }),
    });
  }

  // ------------------------------------------------------------------
  // ApRES Points (scale‑dependent styling)
  // ------------------------------------------------------------------
  const apresSource = new ol.source.Vector();
  const apresStyleCache = {};

  const apresLayer = new ol.layer.Vector({
    source: apresSource,
    style: function (feature, resolution) {
      const radius = Math.max(3, Math.min(10, 8000 / resolution));
      const key = Math.round(radius);

      if (!apresStyleCache[key]) {
        apresStyleCache[key] = new ol.style.Style({
          image: new ol.style.Circle({
            radius: radius,
            fill: new ol.style.Fill({ color: "red" }),
            stroke: new ol.style.Stroke({
              color: "white",
              width: Math.max(1, radius / 3),
            }),
          }),
        });
      }
      return apresStyleCache[key];
    },
    visible: true,
  });

  apresLayer.set("id", "apres");

  fetch("/assets/apres_sites_enriched.geojson")
    .then((r) => {
      if (!r.ok) throw new Error(`GeoJSON HTTP ${r.status}`);
      return r.json();
    })
    .then((json) => {
      const features = new ol.format.GeoJSON().readFeatures(json, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3031",
      });
      console.log("Loaded ApRES features:", features.length);
      apresSource.addFeatures(features);
    })
    .catch((err) => console.error("ApRES load error:", err));

  // ------------------------------------------------------------------
  // MAP
  // ------------------------------------------------------------------
  const map = new ol.Map({
    target,
    layers: [basLayer, apresLayer],
    view: new ol.View({
      projection: projection3031,
      center: [0, 0],
      zoom: 2,
      extent: antarcticaExtent,
    }),
  });

  map.addOverlay(popupOverlay);
  window.__ol_map__ = map;

  // ------------------------------------------------------------------
  // Popup click handler (✅ added)
  // ------------------------------------------------------------------
  map.on("singleclick", function (evt) {
    popupOverlay.setPosition(undefined);
    popupContainer.style.display = "none";

    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      const props = feature.getProperties();

      const site = props.Site || "ApRES Site";
      const pi = props["Principal Investigator"] || "—";
      const email = props.Email || "—";

      popupContent.innerHTML = `
        <div class="popup-title">${site}</div>

        <div>
          <strong>Principal Investigator:</strong><br>
          ${pi}
        </div>

        <div class="popup-email">
          <strong>Email:</strong><br>
          <span class="email-text">${email}</span>
          <button
            class="copy-email-btn"
            data-email="${email}"
            title="Copy email to clipboard"
            aria-label="Copy email"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4
                      a2 2 0 0 1 2-2h9
                      a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
        </div>
      `;

      popupOverlay.setPosition(evt.coordinate);
      popupContainer.style.display = "block";

      return true; // stop after first feature
    });
  });
})();


// --- Copy-to-clipboard handler for popup ---
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".copy-email-btn");
  if (!btn) return;

  const email = btn.dataset.email;
  if (!email) return;

  navigator.clipboard.writeText(email).then(() => {
    btn.textContent = "Copied";
    setTimeout(() => {
      btn.textContent = "Copy";
    }, 1200);
  });
});

// --------------------------------------------------------------------
// Layer visibility control (called from Dash)
// --------------------------------------------------------------------
window.setLayerVisibility = function (layerId, visible) {
  if (!window.__ol_map__) return;

  const layers = window.__ol_map__.getLayers().getArray();

  layers.forEach((layer) => {
    if (layer.get("id") === layerId) {
      layer.setVisible(visible);
    }
  });
};