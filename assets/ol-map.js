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
//
// Mirror of the LAYER_REGISTRY in app.py. Keep these in sync.
// To add a new layer: append one entry here and one in app.py.
//
// Fields:
//   id      – unique per file; used by setLayerVisibility()
//   group   – logical grouping (matches app.py group)
//   file    – GeoJSON filename inside /assets/
//   status  – status label (matches app.py status; used for popup badge)
//   color   – point fill colour
//   visible – initial visibility
//
// GeoJSON feature schema (standard across all files):
//   Name                   – display name in popup
//   Status                 – e.g. "Active", "Wishlist", "Planned"
//   Principal Investigator – PI name
//   Email                  – PI email
//   Event                  – event/voyage identifier
//   description (optional) – freetext shown in popup
// ------------------------------------------------------------------
const LAYER_REGISTRY = [
  {
    id: "scott_base",
    group: "Scott Base",
    file: "scott_base.geojson",
    status: "Active",
    color: "rgba(0, 180, 120, 0.9)",
    visible: true
  },
  {
    id: "arrival_heights",
    group: "Arrival Heights",
    file: "arrival_heights.geojson",
    status: "Active",
    color: "rgba(219, 135, 24, 0.9)",
    visible: true
  },
  {
    id: "asp_planned",
    group: "ASP - Moorings",
    file: "asp_moorings_planned_2027.geojson",
    status: "Planned 2027",
    color: "rgba(30, 144, 255, 0.9)",
    visible: true,
  },
  {
    id: "K082A",
    group: "K082A - Benthic Landers",
    file: "K082A.geojson",
    status: "Active",
    color: "rgba(235, 216, 53, 0.9)",
    visible: true,
  },
  {
    id: "K872B",
    group: "K872B – ApRES",
    file: "K872B.geojson",
    status: "Active",
    color: "rgba(139, 0, 0, 0.95)",
    visible: true,
  },
  {
    id: "K872B_wishlist",
    group: "K872B – ApRES",
    file: "K872B_wishlist.geojson",
    status: "Wishlist",
    color: "rgba(255, 99, 71, 0.85)",
    visible: false,
  },
  {
    id: "K881B",
    group: "K881B - AWS",
    file: "K881B.geojson",
    status: "Active",
    color: "rgba(25, 209, 40, 0.9)",
    visible: true,
  },
  {
    id: "K150A",
    group: "K150A - GNSS & Tide Gauge",
    file: "K150A.geojson",
    status: "Active",
    color: "rgba(27, 57, 189, 0.9)",
    visible: true,
  },
  {
    id: "K102A",
    group: "K102A - Geomagnetic",
    file: "K102A.geojson",
    status: "Active",
    color: "rgba(69, 165, 189, 0.9)",
    visible: true,
  },
  {
    id: "K862A_KIS2",
    group: "K862A - ApRES & GNSS",
    file: "K862A_KIS2.geojson",
    status: "Kamb Ice Stream Site 2",
    color: "rgba(160, 62, 83, 0.9)",
    visible: true,
  },
  {
    id: "K862A_KIS3",
    group: "K862A - ApRES & GNSS",
    file: "K862A_KIS3.geojson",
    status: "Kamb Ice Stream Site 3",
    color: "rgba(69, 165, 189, 0.9)",
    visible: true,
  },
  {
    id: "K862A_CIR",
    group: "KK862A - ApRES & GNSS",
    file: "K862A_CIR.geojson",
    status: "Crary Ice Rise",
    color: "rgba(158, 39, 132, 0.9)",
    visible: true,
  },
  {
    id: "K865A",
    group: "K865A - GNSS",
    file: "K865A.geojson",
    status: "Active",
    color: "rgba(250, 15, 219, 0.9)",
    visible: true,
  },
  {
    id: "K891A",
    group: "K891A - Sea Ice",
    file: "K891A.geojson",
    status: "Active",
    color: "rgba(190, 223, 43, 0.9)",
    visible: true,
  }
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
// Build one OL vector layer from a registry entry
// ------------------------------------------------------------------
function buildLayer(entry) {
  const source = new ol.source.Vector();

  fetch(`/assets/${entry.file}`)
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status} loading ${entry.file}`);
      return r.json();
    })
    .then((json) => {
      const features = new ol.format.GeoJSON().readFeatures(json, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3031",
      });
      console.log(`Loaded "${entry.id}" (${entry.status}): ${features.length} features`);
      source.addFeatures(features);
    })
    .catch((err) => console.error(`Layer "${entry.id}" load error:`, err));

  const layer = new ol.layer.Vector({
    source,
    style: makeScaledPointStyle(entry.color),
    visible: false,  // always start hidden; Dash store sets correct state on load
  });
  layer.set("id", entry.id);
  layer.set("status", entry.status);
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

  const popupContent = document.createElement("div");
  popupContent.className = "ol-popup__content";
  popupContent.id = "ol-popup-content";

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

  // ---- Base tile layer (BAS WMTS) ----------------------------------
  let basLayer;
  try {
    const resp = await fetch(
      "https://tiles.arcgis.com/tiles/tPxy1hrFDhJfZ0Mf/arcgis/rest/services/Antarctica_and_the_Southern_Ocean/MapServer/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"
    );
    const xml = await resp.text();
    const caps = new ol.format.WMTSCapabilities().read(xml);
    const layerName = caps.Contents.Layer[0].Identifier;
    const options = ol.source.WMTS.optionsFromCapabilities(caps, {
      layer: layerName,
      format: "image/png",
      crossOrigin: "anonymous",
    });
    basLayer = new ol.layer.Tile({ source: new ol.source.WMTS(options) });
  } catch (err) {
    console.error("WMTS error:", err);
    basLayer = new ol.layer.Tile({
      source: new ol.source.TileDebug({ projection: projection3031 }),
    });
  }

  // ---- Build all data layers from registry -------------------------
  const dataLayers = LAYER_REGISTRY.map(buildLayer);

  // ---- Map ---------------------------------------------------------
  const map = new ol.Map({
    target,
    layers: [basLayer, ...dataLayers],
    view: new ol.View({
      projection: projection3031,
      center: [0, 0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 9,
      extent: antarcticaExtent,
    }),
  });

  map.addOverlay(popupOverlay);
  window.__ol_map__ = map;

  // ---- Popup helpers -----------------------------------------------

  // Render one feature's details into popupContent
  function renderFeaturePage(props, pageIndex, total) {
    const site        = props.name || "Location";
    const description = props.description || null;
    const event       = props.event || null;
    const statusRaw   = props.status || "—";
    const pi          = props["principal investigator"] || "—";
    const email       = props.email || "—";

    const statusLower = String(statusRaw).toLowerCase();
    const badgeClass  =
      statusLower === "active"   ? "status-badge status-badge--active"   :
      statusLower === "wishlist" ? "status-badge status-badge--wishlist" :
      statusLower === "planned"  ? "status-badge status-badge--planned"  :
                                   "status-badge";

    const site_name      = props.site || null;
    const siteEsc        = escapeHtml(site);
    const statusEsc      = escapeHtml(statusRaw);
    const piEsc          = escapeHtml(pi);
    const emailEsc       = escapeHtml(email);
    const descriptionEsc = description ? escapeHtml(description) : null;
    const eventEsc       = event ? escapeHtml(event) : null;
    const siteNameEsc    = site_name ? escapeHtml(site_name) : null;

    // Pagination controls — only shown when there are multiple features
    const paginationHtml = total > 1 ? `
      <div class="popup-pagination">
        <button class="popup-nav-btn" id="popup-prev" ${pageIndex === 0 ? "disabled" : ""}>&#8592;</button>
        <span class="popup-page-indicator">${pageIndex + 1} / ${total}</span>
        <button class="popup-nav-btn" id="popup-next" ${pageIndex === total - 1 ? "disabled" : ""}>&#8594;</button>
      </div>` : "";

    popupContent.innerHTML = `
      ${paginationHtml}

      <div class="popup-title">${siteEsc}</div>

      ${siteNameEsc ? `
        <div class="popup-site">
          <strong>Site:</strong> ${siteNameEsc}
        </div>` : ""}

      ${descriptionEsc ? `
        <div class="popup-description">
          <strong>Description:</strong> ${descriptionEsc}
        </div>` : ""}

      <div class="popup-status">
        <strong>Status:</strong>
        <span class="${badgeClass}">${statusEsc}</span>
      </div>

      ${eventEsc ? `
        <div class="popup-event">
          <strong>Event:</strong> ${eventEsc}
        </div>` : ""}

      <div class="popup-pi">
        <strong>Principal Investigator:</strong> ${piEsc}
      </div>

      <div class="popup-email">
        <strong>Email:</strong>
        <span class="email-text">${emailEsc}</span>
        <button
          class="copy-email-btn"
          data-email="${emailEsc}"
          title="Copy email to clipboard"
          aria-label="Copy email"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
    `;

    // Wire up prev/next buttons after innerHTML is set
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

  // ---- Popup click handler -----------------------------------------
  map.on("singleclick", function (evt) {
    popupOverlay.setPosition(undefined);
    popupContainer.style.display = "none";

    // Collect all features at the clicked pixel across all visible layers
    const featuresAtPixel = [];
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      featuresAtPixel.push(feature.getProperties());
    });

    if (featuresAtPixel.length === 0) return;

    // Group by coordinate key — features sharing exact coords are paginated together
    const coordKey = (props) => {
      const geom = props.geometry;
      if (!geom) return "unknown";
      const coords = geom.flatCoordinates || geom.getCoordinates();
      return coords[0].toFixed(4) + "," + coords[1].toFixed(4);
    };

    // Use the coordinate of the first hit as the popup anchor, and collect
    // all features that share that exact coordinate
    const firstGeom = featuresAtPixel[0].geometry;
    const firstCoords = firstGeom.flatCoordinates || firstGeom.getCoordinates();
    const anchorKey = firstCoords[0].toFixed(4) + "," + firstCoords[1].toFixed(4);

    const grouped = featuresAtPixel.filter(props => coordKey(props) === anchorKey);

    // Store pagination state globally so nav buttons can access it
    window.__popup_features__ = grouped;
    window.__popup_page__ = 0;

    renderFeaturePage(grouped[0], 0, grouped.length);
    popupOverlay.setPosition(evt.coordinate);
    popupContainer.style.display = "block";
  });
})();

// ---- Copy-to-clipboard -------------------------------------------
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".copy-email-btn");
  if (!btn) return;
  const email = btn.dataset.email;
  if (!email) return;
  navigator.clipboard.writeText(email).then(() => {
    const oldHtml = btn.innerHTML;
    btn.textContent = "Copied";
    setTimeout(() => { btn.innerHTML = oldHtml; }, 1200);
  });
});

// ---- Layer visibility (called from Dash store callback) ----------
window.setLayerVisibility = function (layerId, visible) {
  if (!window.__ol_map__) return;
  window.__ol_map__.getLayers().getArray().forEach((layer) => {
    if (layer.get("id") === layerId) layer.setVisible(!!visible);
  });
};
