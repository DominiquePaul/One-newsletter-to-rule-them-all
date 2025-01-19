'use client';
import { useEffect, useState } from 'react';

export default function Home() {
  // Define state for form fields
  const [email, setEmail] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [interests, setInterests] = useState<string[]>(['Technology']);
  const [newInterest, setNewInterest] = useState('');
  const [frequency, setFrequency] = useState('');

  // Load saved data on component mount
  useEffect(() => {
    const savedData = localStorage.getItem('newsletterPreferences');
    if (savedData) {
      const parsed = JSON.parse(savedData);
      setEmail(parsed.email || '');
      setSelectedSources(parsed.selectedSources || []);
      setInterests(parsed.interests || ['Technology']);
      setFrequency(parsed.frequency || '');
    }
  }, []);

  // Handle form submission
  const handleSave = () => {
    const data = {
      email,
      selectedSources,
      interests,
      frequency
    };
    localStorage.setItem('newsletterPreferences', JSON.stringify(data));
  };

  // Handle adding new interest
  const handleAddInterest = () => {
    if (newInterest && !interests.includes(newInterest)) {
      setInterests([...interests, newInterest]);
      setNewInterest('');
    }
  };

  // Handle removing interest
  const handleRemoveInterest = (interest: string) => {
    setInterests(interests.filter(i => i !== interest));
  };

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <div className="bg-white shadow-md rounded-lg p-8 max-w-2xl mx-auto">
        <div className="space-y-6">
          <h1 className="text-3xl text-teal-800 font-bold mb-4">
            One Newsletter to rule them all
          </h1>

          <div className="space-y-2">
            <label htmlFor="email" className="block font-medium">
              Email address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full p-3 text-lg border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-transparent"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="source" className="block font-medium">
              Select your news sources
            </label>
            <div className="flex flex-wrap gap-2">
              {['nzz', 'economist'].map((source) => (
                <label key={source} className="relative flex items-center">
                  <input
                    type="checkbox"
                    value={source}
                    checked={selectedSources.includes(source)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedSources([...selectedSources, source]);
                      } else {
                        setSelectedSources(selectedSources.filter(s => s !== source));
                      }
                    }}
                    className="peer sr-only"
                    name="sources"
                  />
                  <div className="px-4 py-2 text-lg border border-gray-200 rounded-md cursor-pointer 
                    peer-checked:bg-teal-600 peer-checked:text-white peer-checked:border-transparent
                    hover:bg-gray-50 peer-checked:hover:bg-teal-700 transition-colors">
                    {source === 'nzz' ? 'NZZ' : 'The Economist'}
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="interests" className="block font-medium">
              Your interests
            </label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  placeholder="Add an interest..."
                  className="flex-1 p-3 text-lg border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-transparent"
                />
                <button 
                  onClick={handleAddInterest}
                  className="px-4 py-2 text-lg bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors">
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {interests.map((interest) => (
                  <li key={interest} className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
                    <span>{interest}</span>
                    <button 
                      onClick={() => handleRemoveInterest(interest)}
                      className="text-gray-500 hover:text-red-500">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="frequency" className="block font-medium">
              Newsletter frequency
            </label>
            <select
              id="frequency"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="w-full p-3 text-lg border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-transparent"
            >
              <option value="" disabled>Select frequency</option>
              <option value="daily">Every day</option>
              <option value="weekly">Every week</option>
              <option value="monthly">Every month</option>
            </select>
          </div>

          <button
            onClick={handleSave}
            className="w-full px-4 py-2 text-lg bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}
