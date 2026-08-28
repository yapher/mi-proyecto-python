// static/js/utils/calendar.js
class Calendar {
    constructor(config = {}) {
        if (!config.containerId) throw new Error('Calendar: falta containerId');
        this.config = Object.assign({
            containerId: null,
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1,
            eventos: [],
            onDayClick: null,
            onEventClick: null,
            onToggleRealizado: null,
            dayNames: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            dayClasses: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        }, config);
        this.container = document.getElementById(this.config.containerId);
    }

    render() {
        if (!this.container) return;
        const { year, month, eventos } = this.config;
        const semanas = this._generarSemanas(year, month, eventos);
        
        let html = `<table class="calendar-table table text-white">
            <thead><tr>${this.config.dayNames.map(d => `<th>${d}</th>`).join('')}</tr></thead>
            <tbody>`;
        
        semanas.forEach(semana => {
            html += '<tr>';
            semana.forEach((dia, index) => {
                if (dia.dia === null) {
                    html += '<td><div class="calendar-day empty"></div></td>';
                } else {
                    const clases = this._clasesDia(dia, index);
                    html += `<td>
                        <div class="calendar-day ${clases}" data-fecha="${dia.fecha}"
                             onclick="window.__cal_day__('${dia.fecha}')">
                            <div class="calendar-day-number">${dia.dia}</div>
                            <div class="calendar-events">${this._renderEventos(dia.eventos)}</div>
                        </div>
                    </td>`;
                }
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        this.container.innerHTML = html;
        
        window.__cal_day__ = (fecha) => this.config.onDayClick && this.config.onDayClick(fecha);
        window.__cal_event__ = (json) => {
            if (this.config.onEventClick) this.config.onEventClick(JSON.parse(decodeURIComponent(json)));
        };
        window.__cal_toggle__ = (id, checked, e) => {
            e.stopPropagation();
            if (this.config.onToggleRealizado) this.config.onToggleRealizado(id, checked);
        };
    }

    setEventos(eventos) { this.config.eventos = eventos; this.render(); }
    setFecha(year, month) { this.config.year = year; this.config.month = month; this.render(); }

    _generarSemanas(year, month, eventos) {
        const diasMes = new Date(year, month, 0).getDate();
        const primerDia = (new Date(year, month - 1, 1).getDay() + 6) % 7;
        const hoy = new Date();
        const esHoy = (d) => hoy.getFullYear() === year && (hoy.getMonth() + 1) === month && hoy.getDate() === d;
        
        const porFecha = {};
        eventos.forEach(e => {
            if (e.fecha) (porFecha[e.fecha] = porFecha[e.fecha] || []).push(e);
        });
        
        const semanas = [];
        let semana = [];
        for (let i = 0; i < primerDia; i++) semana.push({ dia: null, fecha: null, eventos: [] });
        
        for (let d = 1; d <= diasMes; d++) {
            const f = `${year}-${String(month).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
            semana.push({ dia: d, fecha: f, esHoy: esHoy(d), eventos: porFecha[f] || [] });
            if (semana.length === 7) { semanas.push(semana); semana = []; }
        }
        if (semana.length) {
            while (semana.length < 7) semana.push({ dia: null, fecha: null, eventos: [] });
            semanas.push(semana);
        }
        return semanas;
    }

    _clasesDia(dia, idx) {
        let c = this.config.dayClasses[idx] || '';
        if (dia.esHoy) c += ' today';
        return c.trim();
    }

    _renderEventos(eventos) {
        if (!eventos || !eventos.length) return '';
        return eventos.map(e => {
            const done = e.realizado ? 'done' : '';
            let prio = '';
            if (!e.realizado) {
                if (e.prioridad === 'alta') prio = 'prio-alta';
                else if (e.prioridad === 'media') prio = 'prio-media';
                else if (e.prioridad === 'baja') prio = 'prio-baja';
            }
            const json = encodeURIComponent(JSON.stringify(e));
            return `<div class="event-pill ${done} ${prio}" onclick="window.__cal_event__('${json}')">
                <input type="checkbox" ${e.realizado ? 'checked' : ''} 
                       onclick="window.__cal_toggle__(${e.id}, this.checked, event)">
                <span>${e.titulo || ''}</span>
            </div>`;
        }).join('');
    }
}
window.Calendar = Calendar;