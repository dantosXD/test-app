import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, userData) => {
        set({ token, user: userData, isAuthenticated: true });
      },
      logout: () => {
        set({ token: null, user: null, isAuthenticated: false });
      },
      setUser: (userData) => {
        set({ user: userData, isAuthenticated: !!get().token }); // Keep isAuthenticated if token exists
      },
      initialize: () => {
        const token = get().token; // Token is already loaded by persist middleware
        if (token) {
          // Potentially fetch user data here if not storing full user object
          // For now, assume user data is stored or re-fetched separately if needed
          // If user object is also in localStorage and loaded by persist, this might be simpler.
          // For this example, we'll rely on the initially persisted user object or
          // expect a separate mechanism to populate user details if only token is stored long-term.
          if (get().user) { // Check if user data was also persisted
            set({ isAuthenticated: true });
          } else {
            // If only token was persisted, or user data is stale/minimal,
            // you might want to fetch user details from backend using the token.
            // For now, if no user data, treat as not fully authenticated or clear session.
            // This part depends on how much user data you persist.
            // Let's assume for now that if a token exists, we might need to re-verify/fetch user.
            // A simple approach: if token exists, assume isAuthenticated true, but user might be minimal.
            set({ isAuthenticated: true }); 
          }
        }
      }
    }),
    {
      name: 'auth-storage', // name of the item in the storage (must be unique)
      storage: createJSONStorage(() => localStorage), // (optional) by default, 'localStorage' is used
      partialize: (state) => ({ token: state.token, user: state.user }), // Persist token and user
    }
  )
);

// Initialize store on load (e.g. to check localStorage)
// This is important for when the app first loads.
useAuthStore.getState().initialize();

export default useAuthStore;
