;;; display-table.rkt

#lang racket

(require racket/format)  ;; ~a

(provide format-field
         format-table/simple
         format-table)

;; A "table" is a list of lists of strings.

(define (transpose table)
  (apply map list table))

(define (get-max-string-length string-list)
  (apply max (map string-length string-list)))

(define (get-max-column-widths table)
  (map get-max-string-length (transpose table)))

(define (format-field field width align)
  (~a #:width width #:align align field))

;; if align is empty then aligments default to right.
(define (normalize table align)
  (let ((max-column-widths (get-max-column-widths table))
        (row-length (length (car table))))
    (map (lambda (row) 
           (map format-field row 
                max-column-widths 
                (if (empty? align)
                    (make-list row-length 'right)
                    align)))
         table)))

(define (joinln list-of-strings)
  (string-join list-of-strings "\n"))

(define (format-table/simple table 
                             #:separator [separator "  "] 
                             #:align [align empty])
  (joinln (map (lambda (row) 
                 (string-join row separator))
               (normalize table align))))

(define (format-table table
                      #:separator [separator "  "]
                      #:align [align empty]
                      #:header-char [header-char false])  
  (let ((normalized-table (normalize table align)))
    (if header-char
        (let* ((header (string-join (first normalized-table)
                                    (make-string (string-length separator) 
                                                 #\Space)))
               (header-underline (make-string (string-length header) 
                                              header-char)))
          (joinln (cons header 
                        (cons header-underline
                              (map (lambda (row)
                                     (string-join row separator)) 
                                   (rest normalized-table))))))
        (joinln (map (lambda (row) 
                       (string-join row separator))
                     normalized-table)))))



