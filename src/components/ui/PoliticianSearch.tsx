'use client';

import React, { useState, useEffect } from 'react';

interface Politician {
  id: number;
  politician: string;
  party: string;
  chamber: string;
  state: string;
  traded_issuer: string;
  ticker: string;
  published_date: string;
  trade_date: string;
  gap_unit: string;
  gap: string;
  trade_type: string;
  trade_size: string;
  page: number;
}

const PoliticianSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [politicians, setPoliticians] = useState<Politician[]>([]);
  const [filteredPoliticians, setFilteredPoliticians] = useState<Politician[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPoliticians = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/Politicians');
        const data = await response.json();
        setPoliticians(data.trades);
        setFilteredPoliticians(data.trades);
      } catch (error) {
        console.error('Error fetching politicians:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPoliticians();
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);

    if (term.trim() === '') {
      setFilteredPoliticians(politicians);
    } else {
      const filtered = politicians.filter((p) =>
        p.politician.toLowerCase().includes(term.toLowerCase())
      );
      setFilteredPoliticians(filtered);
    }
  };

  return (
    <div className="p-4 text-center">
      <h2 className="text-5xl text-white font-bold mb-8">Politician Search</h2>
      <div className="flex justify-center mb-8">
        <input
          type="text"
          placeholder="Search by politician name..."
          value={searchTerm}
          onChange={handleSearch}
          className="border rounded-lg p-4 w-full max-w-2xl bg-gray-800 text-white placeholder-white text-lg"
        />
      </div>
      {loading ? (
        <p className="text-white text-2xl">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredPoliticians.map((p) => (
            <div 
              key={p.id} 
              className={`p-4 rounded-lg shadow-md ${
                p.party === 'Democrat' ? 'bg-blue-900 text-white' : 
                p.party === 'Republican' ? 'bg-red-900 text-white' : 
                'bg-gray-800 text-white'
              }`}
            >
              <h3 className="font-bold text-xl mb-2">{p.politician}</h3>
              <p>Party: {p.party}</p>
              <p>Chamber: {p.chamber}</p>
              <p>State: {p.state}</p>
              <p>Issuer: {p.traded_issuer}</p>
              <p>Ticker: {p.ticker}</p>
              <p>Trade Type: {p.trade_type}</p>
              <p>Trade Size: {p.trade_size}</p>
              <p>Trade Date: {p.trade_date}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PoliticianSearch;
