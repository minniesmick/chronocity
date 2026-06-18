import { CITY_LIST, CITIES } from "@/data/cities";
import { useStore } from "@/store/useStore";
import CityExperience from "@/components/CityExperience";
import "@/App.css";

/**
 * SPRINT 0 shell. Foundation'ın bağlı olduğunu doğrular:
 * tokens.css + fontlar + Zustand store + şehir kayıt defteri.
 * Sprint 2'de IntroScene / GlobeSelector router'ı bunun yerini alır.
 */
export default function App() {
  const activeCity = useStore((s) => s.activeCity);
  const setActiveCity = useStore((s) => s.setActiveCity);

  // Verisi olan şehir seçili → 3D sahne. (Sprint 2'de router/loading araya girer.)
  if (activeCity && CITIES[activeCity].hasBuildingData) {
    return <CityExperience city={activeCity} />;
  }

  return (
    <main className="boot">
      <div className="boot__center">
        <p className="boot__eyebrow">TEKNO-SİNEMATİK · KENTSEL ZAMAN YOLCULUĞU</p>
        <h1 className="boot__wordmark">
          Chrono<span className="boot__accent">City</span>
        </h1>
        <p className="boot__tagline">
          Şehirlerin dönüşümünü zaman içinde 3D gez, her dönemin sesini duy.
        </p>

        <ul className="boot__cities">
          {CITY_LIST.map((city) => {
            const locked = !city.hasBuildingData;
            return (
              <li key={city.id}>
                <button
                  className="city-chip"
                  data-locked={locked}
                  data-active={activeCity === city.id}
                  disabled={locked}
                  onClick={() => setActiveCity(city.id)}
                  style={{ "--chip-color": city.color } as React.CSSProperties}
                >
                  <span className="city-chip__dot" />
                  <span className="city-chip__flag">{city.flag}</span>
                  <span className="city-chip__name">{city.name}</span>
                  <span className="city-chip__status">
                    {locked ? "veri yok" : "hazır"}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>

        <p className="boot__footer">
          SPRINT 0 · foundation hazır
          {activeCity ? ` · seçili: ${activeCity}` : ""}
        </p>
      </div>
    </main>
  );
}
