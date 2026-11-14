import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { api } from "./api.js";

const navigation = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "review", label: "Review queue", icon: "inbox" },
  { id: "invoices", label: "Invoices", icon: "receipt" },
];

function Icon({ name, size = 18 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
  };
  const paths = {
    grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.5" /></>,
    inbox: <><path d="M4 4.5h16l1 11.5H3L4 4.5Z" /><path d="M3.5 15.5h5l1.5 2h4l1.5-2h5" /><path d="M8 9h8" /></>,
    receipt: <><path d="M6 3.5h12v17l-3-1.8-3 1.8-3-1.8-3 1.8v-17Z" /><path d="M9 8h6M9 12h6M9 16h3" /></>,
    upload: <><path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" /><path d="M5 14v5h14v-5" /></>,
    search: <><circle cx="10.8" cy="10.8" r="6.3" /><path d="m16 16 4.5 4.5" /></>,
    arrow: <><path d="M5 12h14m-6-6 6 6-6 6" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    close: <><path d="m6 6 12 12M18 6 6 18" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    file: <><path d="M6 3.5h8l4 4v13H6v-17Z" /><path d="M14 3.5v5h5M9 13h6M9 16h6" /></>,
    spark: <><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" /><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    download: <><path d="M12 4v11m0 0 4-4m-4 4-4-4" /><path d="M5 18v2h14v-2" /></>,
    more: <><circle cx="5" cy="12" r="1" /><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /></>,
  };
  return <svg {...common}>{paths[name] || paths.file}</svg>;
}

function formatMoney(value, currency = "MAD") {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "—";
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: currency || "MAD",
    maximumFractionDigits: 2,
  }).format(amount);
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", year: "numeric" }).format(date);
}

function initials(value) {
  return (value || "?")
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function statusLabel(status) {
  return (status || "pending").replaceAll("_", " ").toLowerCase();
}

function StatusPill({ status }) {
  const state = (status || "").toLowerCase();
  return <span className={`status-pill status-${state}`}>{statusLabel(status)}</span>;
}

function EmptyState({ icon = "file", title, detail, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon"><Icon name={icon} size={22} /></div>
      <strong>{title}</strong>
      <p>{detail}</p>
      {action}
    </div>
  );
}

function App() {
  const [page, setPage] = useState("overview");
  const [jobs, setJobs] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [clients, setClients] = useState([]);
  const [apiStatus, setApiStatus] = useState("checking");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState(null);
  const [search, setSearch] = useState("");
  const [reviewDraft, setReviewDraft] = useState(null);
  const [entityType, setEntityType] = useState(null);
  const [detailInvoice, setDetailInvoice] = useState(null);
  const fileInput = useRef(null);
  const draftJobStatuses = useRef(new Map());

  const refresh = useCallback(async (initial = false, reloadDrafts = false) => {
    if (initial) setLoading(true);
    try {
      const [nextJobs, nextInvoices, nextSuppliers, nextClients] = await Promise.all([
        api.jobs(),
        api.invoices(),
        api.suppliers(),
        api.clients(),
      ]);
      setJobs(nextJobs);
      setInvoices(nextInvoices);
      setSuppliers(nextSuppliers);
      setClients(nextClients);
      setApiStatus("online");

      const jobsToLoadDrafts = nextJobs.filter((job) => (
        initial
        || reloadDrafts
        || ["PENDING", "PROCESSING"].includes(job.status)
        || draftJobStatuses.current.get(job.id) !== job.status
      ));
      if (jobsToLoadDrafts.length > 0) {
        const draftLists = await Promise.all(
          jobsToLoadDrafts.map((job) => api.drafts(job.id).catch(() => [])),
        );
        const refreshedJobIds = new Set(jobsToLoadDrafts.map((job) => job.id));
        setDrafts((current) => [
          ...current.filter((draft) => !refreshedJobIds.has(draft.processing_job_id)),
          ...draftLists.flat(),
        ]);
        for (const job of jobsToLoadDrafts) {
          draftJobStatuses.current.set(job.id, job.status);
        }
      }
    } catch (error) {
      setApiStatus("offline");
      if (initial) setNotice({ type: "error", text: error.message });
    } finally {
      if (initial) setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh(true);
    const timer = window.setInterval(() => refresh(false), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    if (!notice) return undefined;
    const timer = window.setTimeout(() => setNotice(null), 4200);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const pendingDrafts = useMemo(
    () => drafts.filter((draft) => draft.status === "PENDING_REVIEW"),
    [drafts],
  );
  const completedJobs = jobs.filter((job) => job.status === "COMPLETED").length;
  const totalValue = invoices.reduce((sum, invoice) => sum + Number(invoice.total || 0), 0);
  const today = new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(new Date()).toUpperCase();

  async function handleUpload(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setNotice({ type: "error", text: "Choose a ZIP file containing your invoices." });
      return;
    }
    setUploading(true);
    try {
      const job = await api.upload(file);
      setNotice({ type: "success", text: `${job.original_filename} is in the processing queue.` });
      setPage("overview");
      await refresh(false);
    } catch (error) {
      setNotice({ type: "error", text: error.message });
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function openReview(draft) {
    try {
      const fullDraft = await api.draft(draft.id);
      setReviewDraft(fullDraft);
    } catch (error) {
      setNotice({ type: "error", text: error.message });
    }
  }

  async function persistDraft(draftId, body) {
    const updated = await api.saveDraft(draftId, body);
    setReviewDraft(updated);
    setDrafts((current) => current.map((draft) => draft.id === updated.id ? updated : draft));
    await refresh(false);
    return updated;
  }

  async function createEntity(type, values) {
    try {
      const created = type === "supplier"
        ? await api.createSupplier(values)
        : await api.createClient(values);
      if (type === "supplier") {
        setSuppliers((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)));
      } else {
        setClients((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)));
      }
      setNotice({ type: "success", text: `${created.name} added.` });
      return created;
    } catch (error) {
      setNotice({ type: "error", text: error.message });
      return null;
    }
  }

  const pageTitle = navigation.find((item) => item.id === page)?.label || "Overview";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); setPage("overview"); }}>
          <span className="brand-mark"><Icon name="receipt" size={21} /></span>
          <span className="brand-name">papertrail<span>.</span></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="side-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              className={`nav-item ${page === item.id ? "active" : ""}`}
              key={item.id}
              onClick={() => setPage(item.id)}
            >
              <Icon name={item.icon} size={18} />
              <span>{item.label}</span>
              {item.id === "review" && pendingDrafts.length > 0 && (
                <span className="nav-count">{pendingDrafts.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="tip-card">
            <div className="tip-icon"><Icon name="spark" size={18} /></div>
            <strong>Less admin, more flow.</strong>
            <p>Drop in a ZIP and let AI do the busywork.</p>
          </div>
          <div className="user-card">
            <div className="avatar">OA</div>
            <div className="user-info"><strong>Workspace</strong><span>Invoice team</span></div>
            <Icon name="more" size={18} />
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs"><span>Workspace</span><span className="crumb-divider">/</span><strong>{pageTitle}</strong></div>
          <div className="topbar-actions">
            <span className={`api-indicator ${apiStatus}`}><i />{apiStatus === "online" ? "API connected" : apiStatus === "checking" ? "Connecting…" : "API unavailable"}</span>
            <button className="icon-button" aria-label="Search" onClick={() => { if (page === "overview") setPage("review"); window.setTimeout(() => document.getElementById("global-search")?.focus(), 0); }}><Icon name="search" /></button>
            <div className="avatar top-avatar">OA</div>
          </div>
        </header>

        <div className="content">
          {page === "overview" && (
            <Overview
              jobs={jobs}
              pendingDrafts={pendingDrafts}
              invoices={invoices}
              totalValue={totalValue}
              completedJobs={completedJobs}
              loading={loading}
              uploading={uploading}
              fileInput={fileInput}
              onUpload={handleUpload}
              onReview={openReview}
              onNavigate={setPage}
              today={today}
            />
          )}
          {page === "review" && (
            <ReviewQueue
              drafts={pendingDrafts}
              search={search}
              onSearch={setSearch}
              loading={loading}
              onReview={openReview}
              onUploadClick={() => fileInput.current?.click()}
            />
          )}
          {page === "invoices" && (
            <InvoicesPage
              invoices={invoices}
              suppliers={suppliers}
              clients={clients}
              search={search}
              onSearch={setSearch}
              onOpen={setDetailInvoice}
            />
          )}
        </div>
      </main>

      <input
        ref={fileInput}
        className="visually-hidden"
        type="file"
        accept=".zip,application/zip"
        onChange={(event) => handleUpload(event.target.files?.[0])}
      />

      {notice && (
        <div className={`toast toast-${notice.type}`} role="status">
          <Icon name={notice.type === "success" ? "check" : "close"} size={17} />
          <span>{notice.text}</span>
          <button aria-label="Dismiss" onClick={() => setNotice(null)}><Icon name="close" size={15} /></button>
        </div>
      )}

      {reviewDraft && (
        <ReviewModal
          draft={reviewDraft}
          suppliers={suppliers}
          clients={clients}
          onClose={() => setReviewDraft(null)}
          onSave={persistDraft}
          onConfirm={async (draftId, body) => {
            try {
              await api.confirmDraft(draftId, body);
              setReviewDraft(null);
              setNotice({ type: "success", text: "Invoice confirmed and added to your invoices." });
              await refresh(false, true);
            } catch (error) {
              setNotice({ type: "error", text: error.message });
            }
          }}
          onAddEntity={(type, onCreated) => setEntityType({ type, onCreated })}
          onNotice={setNotice}
        />
      )}
      {entityType && (
        <EntityModal
          type={entityType.type}
          onClose={() => setEntityType(null)}
          onCreate={async (values) => {
            const created = await createEntity(entityType.type, values);
            if (created) {
              entityType.onCreated(created);
              setEntityType(null);
            }
          }}
        />
      )}
      {detailInvoice && (
        <InvoiceModal
          invoice={detailInvoice}
          supplier={suppliers.find((item) => item.id === detailInvoice.supplier_id)}
          client={clients.find((item) => item.id === detailInvoice.client_id)}
          onClose={() => setDetailInvoice(null)}
        />
      )}
    </div>
  );
}

function Overview({ jobs, pendingDrafts, invoices, totalValue, completedJobs, loading, uploading, fileInput, onUpload, onReview, onNavigate, today }) {
  const recentJobs = jobs.slice(0, 5);
  return (
    <>
      <section className="page-heading">
        <div><p className="eyebrow">{today}</p><h1>Invoice overview<span>.</span></h1><p className="page-subtitle">Here’s what’s happening with your invoices today.</p></div>
        <button className="button button-primary" onClick={() => fileInput.current?.click()} disabled={uploading}>
          <Icon name="plus" size={17} />{uploading ? "Uploading…" : "Upload invoices"}
        </button>
      </section>

      <section
        className="upload-banner"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => { event.preventDefault(); onUpload(event.dataTransfer.files?.[0]); }}
      >
        <div className="upload-art"><div className="upload-art-sheet"><Icon name="receipt" size={25} /></div><span className="upload-art-spark"><Icon name="spark" size={17} /></span></div>
        <div className="upload-banner-copy"><span className="upload-kicker">YOUR PAPERWORK, ON AUTOPILOT</span><h2>Turn a pile of invoices into a clear picture.</h2><p>Upload a ZIP of PDFs or images. We’ll extract the details and get them ready for your review.</p></div>
        <button className="button button-dark" onClick={() => fileInput.current?.click()} disabled={uploading}><Icon name="upload" size={17} />{uploading ? "Uploading…" : "Choose a ZIP file"}</button>
        <span className="upload-hint">PDF, JPG, PNG · Up to 100 MB</span>
      </section>

      <section className="stats-grid">
        <StatCard label="Waiting for review" value={loading ? "—" : pendingDrafts.length} detail="Invoices ready for a quick check" icon="inbox" tone="lavender" action={() => onNavigate("review")} />
        <StatCard label="Confirmed invoices" value={loading ? "—" : invoices.length} detail={`${completedJobs} completed ${completedJobs === 1 ? "batch" : "batches"}`} icon="receipt" tone="mint" />
        <StatCard label="Total invoiced" value={loading ? "—" : formatMoney(totalValue)} detail="Across confirmed invoices" icon="spark" tone="peach" />
      </section>

      <section className="home-grid">
        <div className="panel jobs-panel">
          <div className="panel-heading"><div><h2>Recent uploads</h2><p>Your latest invoice batches</p></div><button className="text-button" onClick={() => onNavigate("review")}>View queue <Icon name="arrow" size={15} /></button></div>
          {loading ? <LoadingRows /> : recentJobs.length === 0 ? (
            <EmptyState icon="upload" title="No uploads yet" detail="Upload a ZIP file to see processing progress here." />
          ) : (
            <div className="job-list">
              {recentJobs.map((job) => (
                <button className="job-row" key={job.id} onClick={() => onNavigate("review")}>
                  <div className="file-icon"><Icon name="file" size={19} /></div>
                  <div className="job-main"><strong>{job.original_filename}</strong><span>{formatDate(job.created_at)} · {job.total_files || "—"} files</span></div>
                  <div className="job-progress"><div className="progress-track"><span style={{ width: `${job.total_files ? Math.min(100, ((job.processed_files + job.failed_files) / job.total_files) * 100) : 0}%` }} /></div><small>{job.processed_files + job.failed_files}/{job.total_files || 0} processed</small></div>
                  <StatusPill status={job.status} />
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="panel review-panel">
          <div className="panel-heading"><div><h2>Needs your attention</h2><p>Review before these are filed</p></div><span className="attention-count">{pendingDrafts.length}</span></div>
          {pendingDrafts.length === 0 ? (
            <EmptyState icon="check" title="You’re all caught up" detail="New invoices will show up here when extraction is complete." />
          ) : (
            <div className="attention-list">
              {pendingDrafts.slice(0, 4).map((draft) => {
                const data = draft.extracted_data || {};
                return <button className="attention-item" key={draft.id} onClick={() => onReview(draft)}>
                  <span className="attention-file"><Icon name="file" size={17} /></span>
                  <span className="attention-copy"><strong>{data.supplier_name || draft.source_filename}</strong><small>{data.invoice_number || "Invoice needs details"} · {formatMoney(data.reconciliation?.calculated_total, data.currency)}</small></span>
                  <Icon name="arrow" size={16} />
                </button>;
              })}
              {pendingDrafts.length > 4 && <button className="text-button all-reviews" onClick={() => onNavigate("review")}>See all {pendingDrafts.length} invoices <Icon name="arrow" size={15} /></button>}
            </div>
          )}
        </div>
      </section>
    </>
  );
}

function StatCard({ label, value, detail, icon, tone, action }) {
  return <button className={`stat-card stat-${tone} ${action ? "stat-clickable" : ""}`} onClick={action}>
    <div className="stat-top"><span>{label}</span><i><Icon name={icon} size={18} /></i></div>
    <strong className="stat-value">{value}</strong>
    <small>{detail}</small>
  </button>;
}

function LoadingRows() {
  return <div className="skeleton-list"><span /><span /><span /></div>;
}

function ReviewQueue({ drafts, search, onSearch, loading, onReview, onUploadClick }) {
  const filtered = drafts.filter((draft) => {
    const data = draft.extracted_data || {};
    const text = `${data.supplier_name || ""} ${data.invoice_number || ""} ${draft.source_filename || ""}`.toLowerCase();
    return text.includes(search.toLowerCase());
  });
  return <>
    <section className="page-heading compact-heading"><div><p className="eyebrow">INVOICE WORKFLOW</p><h1>Review queue</h1><p className="page-subtitle">Check extracted details and confirm invoices when they’re ready.</p></div><button className="button button-primary" onClick={onUploadClick}><Icon name="plus" size={17} />Upload invoices</button></section>
    <div className="filter-row"><div className="search-box"><Icon name="search" size={17} /><input id="global-search" value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Search invoices or suppliers" /></div><span className="results-count">{filtered.length} {filtered.length === 1 ? "invoice" : "invoices"}</span></div>
    {loading ? <LoadingRows /> : filtered.length === 0 ? (
      <div className="panel"><EmptyState icon="inbox" title={search ? "No matching invoices" : "Nothing to review"} detail={search ? "Try a different supplier or invoice number." : "Once an invoice batch is processed, its drafts will appear here."} /></div>
    ) : (
      <div className="review-grid">{filtered.map((draft) => {
        const data = draft.extracted_data || {};
        const errors = draft.validation_errors || [];
        return <article className="review-card" key={draft.id}>
          <div className="review-card-top"><span className="review-doc-icon"><Icon name="receipt" size={19} /></span><StatusPill status={draft.status} /></div>
          <h3>{data.supplier_name || "Unknown supplier"}</h3>
          <p className="review-invoice-id">{data.invoice_number || draft.source_filename}</p>
          <div className="review-data">
            <div><span>Invoice date</span><strong>{formatDate(data.invoice_date)}</strong></div>
            <div><span>Extracted total</span><strong>{formatMoney(data.reconciliation?.calculated_total, data.currency)}</strong></div>
          </div>
          {errors.length > 0 && <div className="review-warning"><span className="warning-dot" />{errors.length} {errors.length === 1 ? "detail needs" : "details need"} attention</div>}
          <button className="button button-review" onClick={() => onReview(draft)}>Review invoice <Icon name="arrow" size={16} /></button>
        </article>;
      })}</div>
    )}
  </>;
}

function InvoicesPage({ invoices, suppliers, clients, search, onSearch, onOpen }) {
  const filtered = invoices.filter((invoice) => {
    const supplier = suppliers.find((item) => item.id === invoice.supplier_id)?.name || "";
    const client = clients.find((item) => item.id === invoice.client_id)?.name || "";
    return `${invoice.invoice_number} ${supplier} ${client}`.toLowerCase().includes(search.toLowerCase());
  });
  return <>
    <section className="page-heading compact-heading"><div><p className="eyebrow">YOUR RECORDS</p><h1>Invoices</h1><p className="page-subtitle">Every confirmed invoice, all in one place.</p></div></section>
    <div className="filter-row"><div className="search-box"><Icon name="search" size={17} /><input id="global-search" value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Search by number, supplier or client" /></div><span className="results-count">{filtered.length} total</span></div>
    <div className="panel table-panel">
      {filtered.length === 0 ? <EmptyState icon="receipt" title="No invoices here yet" detail="Confirmed invoices will appear here after you review a draft." /> : (
        <div className="table-scroll"><table><thead><tr><th>Invoice</th><th>Supplier</th><th>Client</th><th>Date</th><th>Status</th><th className="amount-cell">Total</th><th /></tr></thead><tbody>
          {filtered.map((invoice) => {
            const supplier = suppliers.find((item) => item.id === invoice.supplier_id);
            const client = clients.find((item) => item.id === invoice.client_id);
            return <tr key={invoice.id} onClick={() => onOpen(invoice)} tabIndex="0" onKeyDown={(event) => { if (event.key === "Enter") onOpen(invoice); }}>
              <td><strong className="invoice-number">{invoice.invoice_number}</strong><small>{invoice.items?.length || 0} line items</small></td>
              <td><div className="entity-cell"><span className="entity-avatar">{initials(supplier?.name)}</span>{supplier?.name || "—"}</div></td>
              <td>{client?.name || "—"}</td><td>{formatDate(invoice.invoice_date)}</td><td><StatusPill status={invoice.status} /></td><td className="amount-cell">{formatMoney(invoice.total, invoice.currency)}</td><td><Icon name="arrow" size={16} /></td>
            </tr>;
          })}
        </tbody></table></div>
      )}
    </div>
  </>;
}

function ReviewModal({ draft, suppliers, clients, onClose, onSave, onConfirm, onAddEntity, onNotice }) {
  const extracted = draft.extracted_data || {};
  const [form, setForm] = useState({
    supplierName: extracted.supplier_name || "",
    clientName: extracted.client_name || "",
    invoiceNumber: extracted.invoice_number || "",
    invoiceDate: (extracted.invoice_date || "").slice(0, 10),
    dueDate: (extracted.due_date || "").slice(0, 10),
    currency: (extracted.currency || "MAD").toUpperCase(),
    notes: draft.notes || extracted.notes || "",
    supplierId: suppliers.find((item) => item.name.toLowerCase() === (extracted.supplier_name || "").toLowerCase())?.id || "",
    clientId: clients.find((item) => item.name.toLowerCase() === (extracted.client_name || "").toLowerCase())?.id || "",
    items: (extracted.items || []).map((item) => ({
      description: item.description || "",
      quantity: item.quantity ?? "",
      unit_price: item.unit_price ?? "",
      tax_rate: item.tax_rate ?? 0,
      product_code: item.product_code || "",
    })),
  });
  const [saving, setSaving] = useState(false);

  function change(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }
  function changeItem(index, field, value) {
    setForm((current) => ({
      ...current,
      items: current.items.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item),
    }));
  }
  function addItem() {
    setForm((current) => ({ ...current, items: [...current.items, { description: "", quantity: "1", unit_price: "0", tax_rate: "0", product_code: "" }] }));
  }
  function removeItem(index) {
    setForm((current) => ({ ...current, items: current.items.filter((_, itemIndex) => itemIndex !== index) }));
  }

  const dataForSave = {
    ...extracted,
    supplier_name: form.supplierName,
    client_name: form.clientName,
    invoice_number: form.invoiceNumber,
    invoice_date: form.invoiceDate,
    due_date: form.dueDate || null,
    currency: form.currency,
    notes: form.notes,
    items: form.items,
  };

  async function save() {
    setSaving(true);
    try {
      await onSave(draft.id, { extracted_data: dataForSave, notes: form.notes || null });
      onNotice({ type: "success", text: "Draft saved." });
    } catch (error) {
      onNotice({ type: "error", text: error.message });
    } finally {
      setSaving(false);
    }
  }

  async function confirm() {
    if (!form.supplierId || !form.clientId) {
      onNotice({ type: "error", text: "Choose or add a supplier and client before confirming." });
      return;
    }
    if (!form.invoiceNumber.trim() || !form.invoiceDate) {
      onNotice({ type: "error", text: "Invoice number and invoice date are required." });
      return;
    }
    if (!form.items.length || form.items.some((item) => !item.description.trim() || Number(item.quantity) <= 0 || Number(item.unit_price) < 0)) {
      onNotice({ type: "error", text: "Add valid descriptions, quantities and prices to every line item." });
      return;
    }
    setSaving(true);
    try {
      await onSave(draft.id, { extracted_data: dataForSave, notes: form.notes || null });
      await onConfirm(draft.id, {
        supplier_id: form.supplierId,
        client_id: form.clientId,
        invoice_number: form.invoiceNumber.trim(),
        invoice_date: form.invoiceDate,
        due_date: form.dueDate || null,
        currency: form.currency,
        notes: form.notes || null,
        items: form.items.map((item) => ({
          description: item.description.trim(),
          quantity: String(item.quantity),
          unit_price: String(item.unit_price),
          tax_rate: String(item.tax_rate || 0),
          product_code: item.product_code || null,
        })),
      });
    } finally {
      setSaving(false);
    }
  }

  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="review-modal" role="dialog" aria-modal="true" aria-labelledby="review-title">
      <header className="modal-header"><div className="modal-title-wrap"><span className="modal-icon"><Icon name="receipt" size={19} /></span><div><p className="eyebrow">DRAFT REVIEW</p><h2 id="review-title">{draft.source_filename}</h2></div></div><button className="icon-button" aria-label="Close" onClick={onClose}><Icon name="close" /></button></header>
      <div className="modal-scroll">
        {(draft.validation_errors || []).length > 0 && <div className="validation-callout"><Icon name="spark" size={17} /><div><strong>Give these details a quick look</strong><ul>{draft.validation_errors.map((error) => <li key={error}>{error}</li>)}</ul></div></div>}
        <div className="form-section"><div className="section-title"><div><h3>Invoice details</h3><p>Confirm the information extracted from this document.</p></div></div>
          <div className="form-grid">
            <label className="field wide-field"><span>Supplier</span><div className="select-with-add"><select value={form.supplierId} onChange={(event) => change("supplierId", event.target.value)}><option value="">Select a supplier</option>{suppliers.map((supplier) => <option key={supplier.id} value={supplier.id}>{supplier.name}</option>)}</select><button type="button" className="small-add" onClick={() => onAddEntity("supplier", (created) => { change("supplierId", created.id); change("supplierName", created.name); })}><Icon name="plus" size={14} /> Add</button></div>{form.supplierName && <small className="extracted-hint">Extracted: {form.supplierName}</small>}</label>
            <label className="field wide-field"><span>Client</span><div className="select-with-add"><select value={form.clientId} onChange={(event) => change("clientId", event.target.value)}><option value="">Select a client</option>{clients.map((client) => <option key={client.id} value={client.id}>{client.name}</option>)}</select><button type="button" className="small-add" onClick={() => onAddEntity("client", (created) => { change("clientId", created.id); change("clientName", created.name); })}><Icon name="plus" size={14} /> Add</button></div>{form.clientName && <small className="extracted-hint">Extracted: {form.clientName}</small>}</label>
            <label className="field"><span>Invoice number</span><input value={form.invoiceNumber} onChange={(event) => change("invoiceNumber", event.target.value)} placeholder="INV-0001" /></label>
            <label className="field"><span>Currency</span><select value={form.currency} onChange={(event) => change("currency", event.target.value)}>{["MAD", "USD", "EUR", "GBP", "CAD"].map((currency) => <option key={currency}>{currency}</option>)}</select></label>
            <label className="field"><span>Invoice date</span><input type="date" value={form.invoiceDate} onChange={(event) => change("invoiceDate", event.target.value)} /></label>
            <label className="field"><span>Due date <em>Optional</em></span><input type="date" value={form.dueDate} onChange={(event) => change("dueDate", event.target.value)} /></label>
          </div>
        </div>
        <div className="form-section line-items-section"><div className="section-title"><div><h3>Line items <span className="item-count">{form.items.length}</span></h3><p>Adjust quantities, prices and tax rates.</p></div><button className="small-add" onClick={addItem}><Icon name="plus" size={14} /> Add item</button></div>
          {form.items.length === 0 ? <div className="no-items">No line items yet. Add one to continue.</div> : <div className="line-items">
            {form.items.map((item, index) => <div className="line-item-row" key={`${index}-${item.product_code}`}>
              <div className="item-index">{String(index + 1).padStart(2, "0")}</div>
              <label className="field item-description"><span>Description</span><input value={item.description} onChange={(event) => changeItem(index, "description", event.target.value)} placeholder="Item description" /></label>
              <label className="field item-quantity"><span>Qty</span><input type="number" min="0.001" step="any" value={item.quantity} onChange={(event) => changeItem(index, "quantity", event.target.value)} /></label>
              <label className="field item-price"><span>Unit price</span><input type="number" min="0" step="any" value={item.unit_price} onChange={(event) => changeItem(index, "unit_price", event.target.value)} /></label>
              <label className="field item-tax"><span>Tax %</span><input type="number" min="0" max="100" step="any" value={item.tax_rate} onChange={(event) => changeItem(index, "tax_rate", event.target.value)} /></label>
              <button className="remove-item" aria-label="Remove line item" onClick={() => removeItem(index)}><Icon name="close" size={15} /></button>
            </div>)}
          </div>}
        </div>
        <label className="field notes-field"><span>Notes <em>Optional</em></span><textarea rows="2" value={form.notes} onChange={(event) => change("notes", event.target.value)} placeholder="Add a note for your records" /></label>
        <div className="modal-total"><span>Calculated total</span><strong>{formatMoney(form.items.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0) * (1 + (Number(item.tax_rate) || 0) / 100), 0), form.currency)}</strong></div>
      </div>
      <footer className="modal-footer"><span className="save-hint">You can edit this later.</span><div><button className="button button-secondary" onClick={save} disabled={saving}>Save draft</button><button className="button button-primary" onClick={confirm} disabled={saving}><Icon name="check" size={17} />{saving ? "Saving…" : "Confirm invoice"}</button></div></footer>
    </section>
  </div>;
}

function EntityModal({ type, onClose, onCreate }) {
  const [name, setName] = useState("");
  const [taxId, setTaxId] = useState("");
  const [busy, setBusy] = useState(false);
  const label = type === "supplier" ? "supplier" : "client";
  async function submit(event) {
    event.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    await onCreate({ name: name.trim(), tax_id: taxId.trim() || null });
    setBusy(false);
  }
  return <div className="modal-backdrop top-modal" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <form className="entity-modal" onSubmit={submit} role="dialog" aria-modal="true" aria-labelledby="entity-title">
      <div className="modal-header"><div><p className="eyebrow">NEW RECORD</p><h2 id="entity-title">Add {label}</h2></div><button type="button" className="icon-button" aria-label="Close" onClick={onClose}><Icon name="close" /></button></div>
      <label className="field"><span>{label[0].toUpperCase() + label.slice(1)} name</span><input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="Business name" required /></label>
      <label className="field"><span>Tax ID <em>Optional</em></span><input value={taxId} onChange={(event) => setTaxId(event.target.value)} placeholder="Tax identification number" /></label>
      <div className="entity-modal-actions"><button type="button" className="button button-secondary" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={busy}>{busy ? "Adding…" : `Add ${label}`}</button></div>
    </form>
  </div>;
}

function InvoiceModal({ invoice, supplier, client, onClose }) {
  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="invoice-detail-modal" role="dialog" aria-modal="true">
      <header className="modal-header"><div><p className="eyebrow">CONFIRMED INVOICE</p><h2>{invoice.invoice_number}</h2></div><button className="icon-button" aria-label="Close" onClick={onClose}><Icon name="close" /></button></header>
      <div className="invoice-detail-meta"><div><span>Supplier</span><strong>{supplier?.name || "—"}</strong></div><div><span>Client</span><strong>{client?.name || "—"}</strong></div><div><span>Invoice date</span><strong>{formatDate(invoice.invoice_date)}</strong></div><div><span>Status</span><StatusPill status={invoice.status} /></div></div>
      <div className="detail-items"><div className="detail-item detail-item-head"><span>Description</span><span>Qty</span><span>Unit price</span><span>Total</span></div>
        {(invoice.items || []).map((item) => <div className="detail-item" key={item.id}><span>{item.description}</span><span>{item.quantity}</span><span>{formatMoney(item.unit_price, invoice.currency)}</span><strong>{formatMoney(item.line_total, invoice.currency)}</strong></div>)}
      </div>
      <div className="detail-summary"><div><span>Subtotal</span><span>{formatMoney(invoice.subtotal, invoice.currency)}</span></div><div><span>Tax</span><span>{formatMoney(invoice.tax_total, invoice.currency)}</span></div><div className="detail-grand-total"><strong>Total</strong><strong>{formatMoney(invoice.total, invoice.currency)}</strong></div></div>
    </section>
  </div>;
}

export default App;
