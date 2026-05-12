"""
Script de test rapide pour la segmentation des anomalies cutanées
"""
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from modules.skin_anomaly.ai_pipeline import predict_skin_anomaly

def test_segmentation(image_path: str):
    """Test la segmentation sur une image"""
    print(f"\n{'='*60}")
    print(f"TEST DE SEGMENTATION")
    print(f"{'='*60}")
    print(f"Image: {image_path}")
    print(f"{'='*60}\n")
    
    try:
        result = predict_skin_anomaly(image_path)
        
        if "error" in result:
            print(f"❌ ERREUR: {result['error']}")
            return
        
        print(f"✅ ANALYSE RÉUSSIE\n")
        
        # Afficher les résultats
        print(f"🐾 Animal détecté:")
        print(f"   {result['animal_emoji']} {result['animal_label']}")
        print(f"   Confiance: {result['animal_confidence']}%\n")
        
        print(f"🔬 Statut de la peau:")
        print(f"   {result['status_emoji']} {result['status_label']}")
        print(f"   {result['status_description']}")
        print(f"   Confiance: {result['verdict_confidence']}%")
        print(f"   P(Anomalie): {result['p_anomaly']}%")
        print(f"   P(Sain): {result['p_healthy']}%\n")
        
        if result['segmentation_done']:
            print(f"📍 Segmentation:")
            print(f"   Zone affectée: {result['seg_area_pct']}%")
            if result['seg_overlay']:
                print(f"   ✅ Overlay généré (base64)")
            else:
                print(f"   ❌ Pas d'overlay")
        else:
            print(f"📍 Segmentation: Non effectuée (peau saine)")
        
        print(f"\n💡 Recommandation:")
        print(f"   {result['recommendation']}")
        
        print(f"\n{'='*60}")
        print(f"Score combiné: {result['combined_score']}%")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_segmentation.py <chemin_image>")
        print("\nExemple:")
        print("  python test_segmentation.py test_image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ Erreur: Le fichier '{image_path}' n'existe pas")
        sys.exit(1)
    
    test_segmentation(image_path)
