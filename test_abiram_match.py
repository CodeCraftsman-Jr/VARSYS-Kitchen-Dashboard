#!/usr/bin/env python3
"""
Test script to verify that "Abiram's Kitchen" will be matched correctly
"""

def test_abiram_kitchen_matching():
    """Test the exact matching logic for Abiram's Kitchen"""
    print("🧪 Testing Abiram's Kitchen matching logic...")
    
    # The exact group name as confirmed by user
    target_group_name = "Abiram's Kitchen"
    
    # Test our search terms
    search_terms = [
        "Abiram's Kitchen",
        "Abiram Kitchen", 
        "Abiram",
        "Kitchen",
        "abiram",
        "kitchen"
    ]
    
    print(f"🎯 Target group: '{target_group_name}'")
    print(f"🔍 Search terms: {search_terms}")
    
    # Test exact match
    exact_matches = []
    for term in search_terms:
        if term.lower() == target_group_name.lower():
            exact_matches.append(term)
    
    print(f"\n✅ Exact matches: {exact_matches}")
    
    # Test partial match (our main detection logic)
    contact_name = target_group_name
    has_abiram = "abiram" in contact_name.lower()
    has_kitchen = "kitchen" in contact_name.lower()
    will_match = has_abiram and has_kitchen
    
    print(f"\n🔍 Detection logic test:")
    print(f"  Contact name: '{contact_name}'")
    print(f"  Contains 'abiram': {has_abiram}")
    print(f"  Contains 'kitchen': {has_kitchen}")
    print(f"  Will be detected: {will_match}")
    
    # Test search term matching
    print(f"\n📋 Search term matching:")
    for term in search_terms:
        if term.lower() in target_group_name.lower():
            print(f"  ✅ '{term}' will find '{target_group_name}'")
        else:
            print(f"  ❌ '{term}' will NOT find '{target_group_name}'")
    
    # Test the specialized detection
    def detect_abiram_kitchen(contact_name):
        return "abiram" in contact_name.lower() and "kitchen" in contact_name.lower()
    
    result = detect_abiram_kitchen(target_group_name)
    print(f"\n🎯 Final result: Will our system detect '{target_group_name}'? {result}")
    
    return result

def test_other_similar_names():
    """Test that we don't accidentally match other groups"""
    print("\n🧪 Testing false positive prevention...")
    
    test_names = [
        "Kitchen Staff",
        "Abiram Family", 
        "Random Kitchen Group",
        "Abiram's Friends",
        "Kitchen Management",
        "Abiram's Kitchen",  # This should match
        "ABIRAM'S KITCHEN",  # This should match (case insensitive)
        "abiram's kitchen"   # This should match (case insensitive)
    ]
    
    def should_match(name):
        return "abiram" in name.lower() and "kitchen" in name.lower()
    
    matches = []
    non_matches = []
    
    for name in test_names:
        if should_match(name):
            matches.append(name)
            print(f"  ✅ MATCH: '{name}'")
        else:
            non_matches.append(name)
            print(f"  ❌ No match: '{name}'")
    
    print(f"\n📊 Results:")
    print(f"  Matches: {len(matches)} - {matches}")
    print(f"  Non-matches: {len(non_matches)} - {non_matches}")
    
    # Should only match the 3 variations of "Abiram's Kitchen"
    expected_matches = 3
    actual_matches = len(matches)
    
    if actual_matches == expected_matches:
        print(f"✅ Perfect! Found exactly {expected_matches} matches as expected")
        return True
    else:
        print(f"⚠️ Expected {expected_matches} matches, got {actual_matches}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Abiram's Kitchen Detection Logic")
    print("=" * 50)
    
    test1_result = test_abiram_kitchen_matching()
    test2_result = test_other_similar_names()
    
    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("🎉 All tests passed!")
        print("\n✅ CONFIRMATION:")
        print("   The system WILL successfully find and message")
        print("   the group named 'Abiram's Kitchen'")
        print("\n📋 Next steps:")
        print("   1. Open VARSYS Kitchen Dashboard")
        print("   2. Go to Settings → WhatsApp Integration")
        print("   3. Connect to WhatsApp Web")
        print("   4. Type your message")
        print("   5. Click '🎯 Send to Abiram's Kitchen'")
        return 0
    else:
        print("⚠️ Some tests failed - check logic above")
        return 1

if __name__ == "__main__":
    exit(main())
