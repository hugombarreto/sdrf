
#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

#include <iostream>
#include <string>
#include <set>
#include <vector>
#include <stdexcept>

#include "element.h"

class PriorityQueue {
 public:
  typedef std::set<Element> elements_set; // element, event
  typedef std::vector<elements_set::iterator> elements_name_map; // name, element

  PriorityQueue();
  void add(Element element);
  Element pop(lt_time_t current_time);
  Element get_min(lt_time_t current_time);
  elements_set::const_iterator cbegin();
  elements_set::const_iterator cend();
  Element remove(const lt_name_t& name);
  bool empty() const;
  bool element_is_in(const lt_name_t& name) const;
  operator std::string() const;
  void update(lt_time_t current_time);

 private:
  lt_time_t last_time;
  elements_set elements_priority; // sort elements
  elements_name_map elements_name_mapper;
};

#endif // PRIORITY_QUEUE_H
