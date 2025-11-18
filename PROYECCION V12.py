import React, { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Target, Zap } from 'lucide-react';

const SimuladorFinanciero = () => {
  // Estados base
  const [ventasNetas, setVentasNetas] = useState(189878959);
  const [pctCosto, setPctCosto] = useState(47);
  const [nomina, setNomina] = useState(25800000);
  const [pctComisiones, setPctComisiones] = useState(3);
  const [pctFletes, setPctFletes] = useState(6);
  const [rentas, setRentas] = useState(6711000);
  const [otrosGastos, setOtrosGastos] = useState(5446936);
  const [pctGastosFinancieros, setPctGastosFinancieros] = useState(1);

  // Estados para IA
  const [analisisIA, setAnalisisIA] = useState('');
  const [cargandoIA, setCargandoIA] = useState(false);

  // Cálculos principales
  const calculos = useMemo(() => {
    const costo = ventasNetas * (pctCosto / 100);
    const margenBruto = ventasNetas - costo;
    const comisiones = ventasNetas * (pctComisiones / 100);
    const fletes = ventasNetas * (pctFletes / 100);
    const gastoTotal = nomina + comisiones + fletes + rentas + otrosGastos;
    const ebitdaOperativo = margenBruto - gastoTotal;
    const gastosFinancieros = ventasNetas * (pctGastosFinancieros / 100);
    const ebitda = ebitdaOperativo - gastosFinancieros;
    
    const margenBrutoPct = (margenBruto / ventasNetas) * 100;
    const margenEbitdaPct = (ebitda / ventasNetas) * 100;
    
    // Punto de equilibrio
    const gastosOperativosFijos = nomina + rentas + otrosGastos;
    const gastosVariablesPct = pctCosto + pctComisiones + pctFletes;
    const puntoEquilibrio = gastosOperativosFijos / (1 - (gastosVariablesPct / 100));
    
    return {
      costo,
      margenBruto,
      comisiones,
      fletes,
      gastoTotal,
      ebitdaOperativo,
      gastosFinancieros,
      ebitda,
      margenBrutoPct,
      margenEbitdaPct,
      puntoEquilibrio
    };
  }, [ventasNetas, pctCosto, nomina, pctComisiones, pctFletes, rentas, otrosGastos, pctGastosFinancieros]);

  // Generar análisis con IA
  const generarAnalisisIA = async () => {
    setCargandoIA(true);
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{
            role: "user",
            content: `Analiza esta situación financiera de PORTAWARE (fabricante de artículos de plástico para el hogar) y proporciona un análisis ejecutivo conciso (máximo 150 palabras):

Ventas Netas: $${ventasNetas.toLocaleString()}
Costo (${pctCosto}%): $${calculos.costo.toLocaleString()}
Margen Bruto: $${calculos.margenBruto.toLocaleString()} (${calculos.margenBrutoPct.toFixed(1)}%)
Gastos Totales: $${calculos.gastoTotal.toLocaleString()}
- Nómina: $${nomina.toLocaleString()}
- Comisiones (${pctComisiones}%): $${calculos.comisiones.toLocaleString()}
- Fletes (${pctFletes}%): $${calculos.fletes.toLocaleString()}
- Rentas: $${rentas.toLocaleString()}
- Otros: $${otrosGastos.toLocaleString()}
EBITDA Operativo: $${calculos.ebitdaOperativo.toLocaleString()}
Gastos Financieros (${pctGastosFinancieros}%): $${calculos.gastosFinancieros.toLocaleString()}
EBITDA Final: $${calculos.ebitda.toLocaleString()} (${calculos.margenEbitdaPct.toFixed(1)}%)
Punto de Equilibrio: $${calculos.puntoEquilibrio.toLocaleString()}

Proporciona: 1) Diagnóstico de salud financiera, 2) 2-3 recomendaciones específicas para mejorar rentabilidad, 3) Análisis del punto de equilibrio.`
          }]
        })
      });

      const data = await response.json();
      const texto = data.content.find(item => item.type === "text")?.text || "No se pudo generar el análisis";
      setAnalisisIA(texto);
    } catch (error) {
      setAnalisisIA(`Error al generar análisis: ${error.message}`);
    } finally {
      setCargandoIA(false);
    }
  };

  // Escenarios predefinidos
  const aplicarEscenario = (tipo) => {
    switch(tipo) {
      case 'optimista':
        setVentasNetas(189878959 * 1.15);
        setPctCosto(45);
        setPctFletes(5.5);
        setPctGastosFinancieros(0.8);
        break;
      case 'conservador':
        setVentasNetas(189878959 * 0.95);
        setPctCosto(48);
        setPctFletes(6.5);
        break;
      case 'equilibrio':
        setVentasNetas(calculos.puntoEquilibrio);
        break;
      case 'reset':
        setVentasNetas(189878959);
        setPctCosto(47);
        setNomina(25800000);
        setPctComisiones(3);
        setPctFletes(6);
        setRentas(6711000);
        setOtrosGastos(5446936);
        setPctGastosFinancieros(1);
        break;
    }
  };

  // Datos para gráficos
  const datosWaterfall = [
    { name: 'Ventas Netas', valor: ventasNetas, color: '#1F77B4' },
    { name: 'Costo', valor: -calculos.costo, color: '#DC3545' },
    { name: 'Margen Bruto', valor: calculos.margenBruto, color: '#28A745' },
    { name: 'Gastos', valor: -calculos.gastoTotal, color: '#FD7E14' },
    { name: 'EBITDA Op.', valor: calculos.ebitdaOperativo, color: '#6F42C1' },
    { name: 'G. Financieros', valor: -calculos.gastosFinancieros, color: '#DC3545' },
    { name: 'EBITDA', valor: calculos.ebitda, color: '#28A745' }
  ];

  const datosGastos = [
    { name: 'Nómina', value: nomina, color: '#1F77B4' },
    { name: 'Comisiones', value: calculos.comisiones, color: '#FF7F0E' },
    { name: 'Fletes', value: calculos.fletes, color: '#2CA02C' },
    { name: 'Rentas', value: rentas, color: '#D62728' },
    { name: 'Otros', value: otrosGastos, color: '#9467BD' }
  ];

  const formatMoney = (val) => `$${(val / 1000000).toFixed(1)}M`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Simulador Financiero PORTAWARE</h1>
              <p className="text-gray-600">Análisis simplificado con IA integrada</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => aplicarEscenario('optimista')} className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition">
                📈 Optimista
              </button>
              <button onClick={() => aplicarEscenario('conservador')} className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition">
                📉 Conservador
              </button>
              <button onClick={() => aplicarEscenario('equilibrio')} className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                ⚖️ Equilibrio
              </button>
              <button onClick={() => aplicarEscenario('reset')} className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition">
                🔄 Reset
              </button>
            </div>
          </div>
        </div>

        {/* Métricas Clave */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Ventas Netas</span>
              <DollarSign className="text-blue-500" size={20} />
            </div>
            <div className="text-2xl font-bold text-gray-800">{formatMoney(ventasNetas)}</div>
            <div className="text-xs text-gray-500 mt-1">Base de ingresos</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Margen Bruto</span>
              <TrendingUp className="text-green-500" size={20} />
            </div>
            <div className="text-2xl font-bold text-green-600">{calculos.margenBrutoPct.toFixed(1)}%</div>
            <div className="text-xs text-gray-500 mt-1">{formatMoney(calculos.margenBruto)}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">EBITDA</span>
              <Target className="text-purple-500" size={20} />
            </div>
            <div className="text-2xl font-bold text-purple-600">{calculos.margenEbitdaPct.toFixed(1)}%</div>
            <div className="text-xs text-gray-500 mt-1">{formatMoney(calculos.ebitda)}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Punto Equilibrio</span>
              <Zap className="text-orange-500" size={20} />
            </div>
            <div className="text-2xl font-bold text-orange-600">{formatMoney(calculos.puntoEquilibrio)}</div>
            <div className={`text-xs mt-1 ${ventasNetas > calculos.puntoEquilibrio ? 'text-green-600' : 'text-red-600'}`}>
              {ventasNetas > calculos.puntoEquilibrio ? '✓ Por encima' : '✗ Por debajo'}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Panel de Controles */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">🎛️ Controles de Simulación</h2>
            
            <div className="space-y-4">
              {/* Ventas Netas */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Ventas Netas</label>
                <input
                  type="number"
                  value={ventasNetas}
                  onChange={(e) => setVentasNetas(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-500">{formatMoney(ventasNetas)}</span>
              </div>

              {/* % Costo */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">% Costo de Ventas</label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="30"
                    max="70"
                    step="0.5"
                    value={pctCosto}
                    onChange={(e) => setPctCosto(Number(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-bold text-blue-600 w-12">{pctCosto}%</span>
                </div>
                <span className="text-xs text-gray-500">{formatMoney(calculos.costo)}</span>
              </div>

              {/* Nómina */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Nómina</label>
                <input
                  type="number"
                  value={nomina}
                  onChange={(e) => setNomina(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-500">{formatMoney(nomina)}</span>
              </div>

              {/* % Comisiones */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">% Comisiones</label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.25"
                    value={pctComisiones}
                    onChange={(e) => setPctComisiones(Number(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-bold text-blue-600 w-12">{pctComisiones}%</span>
                </div>
                <span className="text-xs text-gray-500">{formatMoney(calculos.comisiones)}</span>
              </div>

              {/* % Fletes */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">% Fletes</label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="15"
                    step="0.25"
                    value={pctFletes}
                    onChange={(e) => setPctFletes(Number(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-bold text-blue-600 w-12">{pctFletes}%</span>
                </div>
                <span className="text-xs text-gray-500">{formatMoney(calculos.fletes)}</span>
              </div>

              {/* Rentas */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Rentas</label>
                <input
                  type="number"
                  value={rentas}
                  onChange={(e) => setRentas(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-500">{formatMoney(rentas)}</span>
              </div>

              {/* Otros Gastos */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Otros Gastos</label>
                <input
                  type="number"
                  value={otrosGastos}
                  onChange={(e) => setOtrosGastos(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-xs text-gray-500">{formatMoney(otrosGastos)}</span>
              </div>

              {/* % Gastos Financieros */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">% Gastos Financieros</label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.1"
                    value={pctGastosFinancieros}
                    onChange={(e) => setPctGastosFinancieros(Number(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-bold text-blue-600 w-12">{pctGastosFinancieros}%</span>
                </div>
                <span className="text-xs text-gray-500">{formatMoney(calculos.gastosFinancieros)}</span>
              </div>
            </div>
          </div>

          {/* Gráficos y Análisis */}
          <div className="col-span-2 space-y-6">
            {/* Puente de Utilidad */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">📊 Puente de Utilidad</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={datosWaterfall}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis tickFormatter={(val) => formatMoney(val)} />
                  <Tooltip formatter={(val) => formatMoney(val)} />
                  <Bar dataKey="valor">
                    {datosWaterfall.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Composición de Gastos */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">🥧 Composición de Gastos</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={datosGastos}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {datosGastos.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(val) => formatMoney(val)} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Análisis IA */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-800">🤖 Análisis Estratégico con IA</h3>
                <button
                  onClick={generarAnalisisIA}
                  disabled={cargandoIA}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400"
                >
                  {cargandoIA ? '⏳ Analizando...' : '🚀 Generar Análisis'}
                </button>
              </div>
              {analisisIA && (
                <div className="bg-white rounded-lg p-4 text-gray-700 whitespace-pre-line">
                  {analisisIA}
                </div>
              )}
              {!analisisIA && !cargandoIA && (
                <div className="text-gray-500 text-center py-8">
                  Haz clic en "Generar Análisis" para obtener recomendaciones estratégicas con IA
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimuladorFinanciero;


