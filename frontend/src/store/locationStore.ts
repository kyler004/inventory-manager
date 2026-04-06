import { create } from 'zustand'

interface LocationState {
    // The currently selected location (for multi-location admins)
    activeLocationId: number | null
    setActivateLocation: (id: number) => void
}

export const useLocationStore = create<LocationState>((set) => ({
    activeLocationId: null, 
    setActivateLocation: (id) => set({ activeLocationId: id}), 
}))