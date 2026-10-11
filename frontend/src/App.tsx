import { useState } from 'react'
import type { FormEvent } from 'react'
import { examples } from './examples'
import type { AnalyzeResponse, RequirementResult } from './types'

type RequestState = 'idle' | 'loading' | 'success' | 'error'

function isAnalyzeResponse(value: unknown): value is AnalyzeResponse {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Partial<AnalyzeResponse>
  return Array.isArray(candidate.requirements)
    && Array.isArray(candidate.learning_plan)
    && typeof candidate.coverage?.supported === 'number'
    && typeof candidate.coverage?.total === 'number'
    && typeof candidate.notice === 'string'
}

function ArrowIcon() {
  return (
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 12h15m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 40 40" fill="none">
        <path d="M5 26c5-10 10-10 15 0s10 10 15 0" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
        <circle cx="8" cy="23" r="2.5" fill="currentColor" />
        <circle cx="32" cy="23" r="2.5" fill="currentColor" />
      </svg>
    </span>
  )
}

function RequirementCard({ item }: { item: RequirementResult }) {
  const supported = item.status === 'supported'
  return (
    <article className={`skill-card ${supported ? 'is-supported' : 'is-open'}`}>
      <div className="skill-card-head">
        <h4>{item.skill}</h4>
        <span className={`status-pill ${supported ? 'status-supported' : 'status-open'}`}>
          <span className="status-dot" />
          {supported ? 'Ada bukti' : 'Belum terbukti'}
        </span>
      </div>
      <div className="evidence-grid">
        <div>
          <span className="eyebrow small">Dari lowongan</span>
          <blockquote>“{item.job_quote}”</blockquote>
        </div>
        <div>
          <span className="eyebrow small">Dari profil</span>
          {item.profile_quote ? (
            <blockquote>“{item.profile_quote}”</blockquote>
          ) : (
            <p className="empty-evidence">Belum ada kutipan yang mendukung.</p>
          )}
        </div>
      </div>
      <p className="skill-reason">{item.reason}</p>
    </article>
  )
}

function Results({ result }: { result: AnalyzeResponse }) {
  return (
    <section className="results section-wrap" id="hasil" aria-live="polite">
      <div className="section-heading result-heading">
        <div>
          <span className="eyebrow">HASIL ANALISIS</span>
          <h2>Peta skill kamu sudah siap.</h2>
          <p>Lihat bukti yang ditemukan, lalu mulai dari langkah belajar yang paling relevan.</p>
        </div>
        <div className="coverage-badge" aria-label={`${result.coverage.supported} dari ${result.coverage.total} syarat memiliki bukti`}>
          <strong>{result.coverage.supported}<span>/{result.coverage.total}</span></strong>
          <small>syarat dengan bukti</small>
        </div>
      </div>

      <div className="result-block">
        <div className="block-heading">
          <span className="step-number">01</span>
          <div>
            <h3>Bukti keterampilan</h3>
            <p>Setiap kesimpulan dapat ditelusuri ke kalimat sumbernya.</p>
          </div>
        </div>
        <div className="skill-list">
          {result.requirements.map((item) => <RequirementCard key={item.requirement_id} item={item} />)}
        </div>
      </div>

      <div className="result-block plan-block">
        <div className="block-heading">
          <span className="step-number">02</span>
          <div>
            <h3>Rencana belajar 7 hari</h3>
            <p>Tugas harian kecil dengan hasil yang bisa ditunjukkan.</p>
          </div>
        </div>
        <div className="plan-grid">
          {result.learning_plan.map((day) => (
            <article className="day-card" key={day.day}>
              <div className="day-top"><span>HARI {String(day.day).padStart(2, '0')}</span><span className="day-line" /></div>
              <h4>{day.focus}</h4>
              <p>{day.action}</p>
              <div className="deliverable"><span>HASIL</span>{day.deliverable}</div>
            </article>
          ))}
        </div>
      </div>
      <p className="notice">{result.notice}</p>
    </section>
  )
}

function App() {
  const [profileText, setProfileText] = useState('')
  const [jobText, setJobText] = useState('')
  const [selectedExample, setSelectedExample] = useState<string | null>(null)
  const [state, setState] = useState<RequestState>('idle')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState('')

  const canSubmit = profileText.trim().length >= 20 && jobText.trim().length >= 50 && state !== 'loading'

  function fillExample(id: string) {
    const example = examples.find((item) => item.id === id)
    if (!example) return
    setProfileText(example.profile)
    setJobText(example.job)
    setSelectedExample(id)
    setResult(null)
    setError('')
    setState('idle')
  }

  function updateInput(field: 'profile' | 'job', value: string) {
    if (field === 'profile') setProfileText(value)
    else setJobText(value)
    setSelectedExample(null)
    setResult(null)
    setError('')
    setState('idle')
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canSubmit) return
    setState('loading')
    setError('')
    setResult(null)
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 120_000)
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_text: profileText.trim(), job_text: jobText.trim() }),
        signal: controller.signal,
      })
      const payload: unknown = await response.json().catch(() => null)
      if (!response.ok) {
        const detail = typeof payload === 'object' && payload !== null && 'detail' in payload
          ? (payload as { detail: unknown }).detail : null
        const message = typeof detail === 'object' && detail !== null && 'message' in detail
          ? String((detail as { message: unknown }).message)
          : 'Analisis belum berhasil. Periksa masukan lalu coba lagi.'
        throw new Error(message)
      }
      if (!isAnalyzeResponse(payload)) {
        throw new Error('Server mengirim hasil yang tidak dapat dibaca. Silakan coba lagi.')
      }
      setResult(payload)
      setState('success')
      window.setTimeout(() => document.getElementById('hasil')?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (cause) {
      setError(cause instanceof DOMException && cause.name === 'AbortError'
        ? 'Analisis terlalu lama. Silakan coba lagi.'
        : cause instanceof Error ? cause.message : 'Terjadi kesalahan yang tidak diketahui.')
      setState('error')
    } finally {
      window.clearTimeout(timeout)
    }
  }

  return (
    <div className="page-shell">
      <header className="site-header section-wrap">
        <a className="brand" href="#beranda" aria-label="SkillBridge AI, kembali ke atas">
          <BrandMark /><span>skillbridge<span className="brand-ai">.ai</span></span>
        </a>
        <nav aria-label="Navigasi utama">
          <a href="#cara-kerja">Cara kerja</a>
          <a className="nav-cta" href="#analisis">Mulai analisis <ArrowIcon /></a>
        </nav>
      </header>

      <main id="beranda">
        <section className="hero section-wrap">
          <div className="hero-copy">
            <span className="hero-kicker"><span className="kicker-spark">✳</span> UNTUK LANGKAH KARIER BERIKUTNYA</span>
            <h1>Dari lowongan,<br /><em>jadi arah belajar.</em></h1>
            <p className="hero-lead">Pahami skill yang sudah kamu buktikan, temukan yang perlu diperkuat, dan mulai dengan rencana belajar tujuh hari.</p>
            <a className="primary-link" href="#analisis">Petakan skill saya <ArrowIcon /></a>
            <div className="hero-meta"><span className="mini-dot" /> Berbasis bukti dari teks yang kamu berikan</div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="orbit orbit-one" /><div className="orbit orbit-two" />
            <div className="art-card art-card-back"><span>LOWONGAN MAGANG</span><i /><i /><i /></div>
            <div className="art-card art-card-front">
              <div className="art-card-top"><span>SKILL MAP</span><span className="art-asterisk">✳</span></div>
              <div className="art-row"><b>SQL</b><span className="art-check">✓</span></div>
              <div className="art-row"><b>Visualisasi data</b><span className="art-check">✓</span></div>
              <div className="art-row"><b>Python</b><span className="art-open">↗</span></div>
              <div className="art-progress"><span /></div>
              <small>Langkah berikutnya sudah terlihat.</small>
            </div>
            <div className="art-stamp">7<br /><span>HARI</span></div>
          </div>
        </section>

        <section className="how-section" id="cara-kerja">
          <div className="section-wrap how-inner">
            <div className="how-intro"><span className="eyebrow">CARA KERJA</span><h2>Tiga langkah.<br />Lebih jelas arahnya.</h2></div>
            <div className="how-steps">
              <div className="how-step"><span>01 / MASUKKAN</span><p>Tulis pengalaman dan tempel lowongan yang kamu incar.</p></div>
              <div className="how-step"><span>02 / COCOKKAN</span><p>Lihat syarat dan bukti yang benar-benar muncul di profil.</p></div>
              <div className="how-step"><span>03 / BERTINDAK</span><p>Ikuti rencana tujuh hari untuk memperkuat portofoliomu.</p></div>
            </div>
          </div>
        </section>

        <section className="workspace section-wrap" id="analisis">
          <div className="section-heading workspace-heading">
            <div><span className="eyebrow">MULAI DI SINI</span><h2>Petakan peluangmu.</h2><p>Gunakan teks anonim. Nama, email, dan nomor telepon tidak diperlukan.</p></div>
            <div className="workspace-icon" aria-hidden="true">↗</div>
          </div>
          <div className="example-section"><span>Coba dengan contoh:</span><div className="example-buttons">
            {examples.map((example) => (
              <button className={`example-button ${selectedExample === example.id ? 'selected' : ''}`} type="button" key={example.id} onClick={() => fillExample(example.id)} title={example.caption}>
                {example.label}
              </button>
            ))}
          </div></div>
          <form className="analysis-form" onSubmit={handleSubmit}>
            <div className="fields-grid">
              <label className="field-card"><span className="field-top"><span className="field-index">A</span><strong>Profil & pengalaman</strong></span><span className="field-help">Ceritakan proyek, alat, dan hasil yang pernah kamu kerjakan.</span>
                <textarea value={profileText} maxLength={10_000} onChange={(event) => updateInput('profile', event.target.value)} placeholder="Contoh: Saya membuat dashboard penjualan menggunakan SQL..." rows={9} required minLength={20} />
                <span className="char-count">{profileText.length.toLocaleString('id-ID')} / 10.000 karakter</span>
              </label>
              <label className="field-card"><span className="field-top"><span className="field-index">B</span><strong>Lowongan magang</strong></span><span className="field-help">Tempel deskripsi pekerjaan beserta syarat keterampilannya.</span>
                <textarea value={jobText} maxLength={10_000} onChange={(event) => updateInput('job', event.target.value)} placeholder="Contoh: Dibutuhkan kemampuan SQL, Python, dan visualisasi data..." rows={9} required minLength={50} />
                <span className="char-count">{jobText.length.toLocaleString('id-ID')} / 10.000 karakter</span>
              </label>
            </div>
            <div className="form-footer"><span>🔒 &nbsp;Teks diproses untuk analisis ini dan tidak disimpan oleh aplikasi.</span><button className="submit-button" type="submit" disabled={!canSubmit}>{state === 'loading' ? <><span className="spinner" /> Sedang menganalisis...</> : <>Analisis sekarang <ArrowIcon /></>}</button></div>
          </form>
          {state === 'error' && <div className="error-banner" role="alert"><strong>Analisis belum selesai.</strong><span>{error}</span></div>}
        </section>
        {result && <Results result={result} />}
      </main>
      <footer className="site-footer"><div className="section-wrap footer-inner"><div className="brand footer-brand"><BrandMark /><span>skillbridge<span className="brand-ai">.ai</span></span></div><p>Temukan bukti. Tentukan langkah.</p><small>Prototipe capstone · React, FastAPI & Gemini</small></div></footer>
    </div>
  )
}

export default App
